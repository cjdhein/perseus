
var crawlerApp = angular.module('crawlerApp', ['ngRoute', 'ngCookies']);

crawlerApp.config(function($routeProvider) {
	$routeProvider

	// route for the home page
	.when('/', {
		templateUrl : './../html/home.html',
		controller  : 'homeController'
	})

	// route for the graph page
	.when('/graph', {
		templateUrl : './../html/graph.html',
		controller  : 'graphController'
	})

	// route for the history page
	.when('/history', {
		templateUrl : './../html/history.html',
		controller  : 'historyController'
	});
});

crawlerApp.factory('graphData', function() {
	var graph = {
		nodes: [],
		edges: []
	};

	return {
    	addNode: addNode,
    	addEdge: addEdge,
    	getGraph: get,
    	reset: reset
	};

	function addNode(node) {
		graph.nodes.push(node);
	}

	function addEdge(begin, end) {
		var edge = {
			from: parseInt(begin),
			to: parseInt(end)
		}
		graph.edges.push(edge);
	}

	function get() {
		return graph;
	}

	function reset() {
		graph.nodes = [];
		graph.edges = [];
	};
});

// create the controller and inject Angular's $scope
crawlerApp.controller('homeController', function($scope, $cookieStore, $http, $location, graphData) {
	$scope.data = {
		search: "dfs"
	};

	var cookieData = $cookieStore.get('graphCrawlerHistoryData');
	var cookie = $cookieStore.get('graphCrawlerHistory');
	if(!cookieData) {
		$cookieStore.put('graphCrawlerHistoryData', {
			start: 0,
			size: 0
		});
		$cookieStore.put('graphCrawlerHistory', {});
	}

	//TODO: Send request to server to retrieve graph from search terms
	$scope.submit = function(){
		if(!$scope.data.start || !$scope.data.search || !$scope.data.limit || !Number.isInteger($scope.data.limit)) {
			return;
		}

		var url = "/post";

		$http.post(url, $scope.data)
			.success(function(response, status){
				graphData.reset();
				saveData(response);
				console.log(graphData.getGraph());
				addCookie($scope.data);

				$location.path('/graph');
			}).
			error(function(data, status){
				//error message
				console.log("error");
			});
	};

	var saveData = function(text) {
		var parser = new DOMParser();
		var xml = parser.parseFromString(text, 'application/xml');
		var pages = xml.getElementsByTagName('page');

		var idToLevel = {
			0: 1
		};

		for(var i = 0; i < pages.length; ++i) {
			var nodes = pages[i].children;
			var newNode = {
				keyword: false
			};

			if(i == 0) {
				newNode["level"] = 1;
			}

			for(var j = 0; j < nodes.length; ++j) {
				if(nodes[j].nodeName == 'parent_id') {
					graphData.addEdge(i, nodes[j].innerHTML);
					idToLevel[i] = idToLevel[nodes[j].innerHTML] + 2;
					newNode["level"] = idToLevel[i]; 
				}
				else if(nodes[j].nodeName == 'keyword') {
					newNode['keyword'] = true;
				}
				else {
					newNode[nodes[j].nodeName] = nodes[j].innerHTML;
				}
			}

			graphData.addNode(newNode);
		}
	};

	var addCookie = function(data) {
		var cookieData = $cookieStore.get('graphCrawlerHistoryData');
		var cookie = $cookieStore.get('graphCrawlerHistory');
		if(cookieData['size'] == 10) {
			cookie[cookieData['start']] = data;
			cookieData['start'] = (cookieData['start'] + 1) % 10;
		}
		else {
			cookie[(cookieData['start']+cookieData['size']) % 10] = data;
			cookieData['size'] += 1;
		}

		$cookieStore.put('graphCrawlerHistoryData', cookieData);
		$cookieStore.put('graphCrawlerHistory', cookie);
	};

	$scope.history = function(){
		$location.path('/history');
	};

});

crawlerApp.controller('graphController', function($scope, graphData) {
	//TODO: Create node and edges from graph service
	var graph = graphData.getGraph();
	var nodes = new vis.DataSet(graph.nodes);
	var edges = new vis.DataSet(graph.edges);

	// create a network
	var container = document.getElementById('mynetwork');

	// provide the data in the vis format
	var data = {
    	nodes: nodes,
    	edges: edges
	};

	var options = {
    	edges: {
        	labelHighlightBold: false,
        	selectionWidth: 0,
    	},
    	layout: {
        	hierarchical: {
            	enabled: true,
            	direction: "LR",
            	//sortMethod: "directed"
        	}
    	},
    	interaction: {
        	dragNodes: false,
       		navigationButtons: true,
    	},
    	physics: {
        	enabled: false
    	}
    };

	// initialize your network!
	var network = new vis.Network(container, data, options);

	//Handle node on-click
	network.on('click', function(properties) {
		document.getElementById("popup").style.display = "none";

		var nodeID = properties.nodes[0];
		console.log("nodeID: " + nodeID);

		if(nodeID) {
			network.focus(nodeID, {
				scale: 1.0,
				animation: true
			}, 1000);

			setTimeout(function(){
				document.getElementById("popup").style.display = "block";
				document.getElementById("pTitle").innerHTML = graph.nodes[nodeID]['title'];
				document.getElementById("pInfo").innerHTML = graph.nodes[nodeID]['info'];
				document.getElementById("pLink").href = graph.nodes[nodeID]['url'];
			}, 1000);
		}
		else {
			document.getElementById('popup').style.display = "none";
		}

	});

	network.on('zoom', function(properties){
		document.getElementById('popup').style.display = "none";
	});

	network.on('dragStart', function(properties){
		document.getElementById('popup').style.display = "none";
	});
});

crawlerApp.controller('historyController', function($scope, $cookieStore, $location) {
	var historyArr = [];
	var cookieData = $cookieStore.get('graphCrawlerHistoryData');
	var start = cookieData['start'];
	var size = cookieData['size'];
	var cookie = $cookieStore.get('graphCrawlerHistory');

	for(var i = 0; i < size; ++i) {
		historyArr.push(cookie[(start+i)%10]);
	}

	$scope.hist = historyArr.reverse();

	$scope.view = function(id){
		console.log(id);
		//Send request to server
		//update graph
		//$location.path('/graph');
	};

	$scope.search = function() {
		$location.path('/');
	};
});












































