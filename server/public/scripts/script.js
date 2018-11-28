const keywordColor = "#ff7070";
const defaultColor = "#D2E5FF";

var crawlerApp = angular.module('crawlerApp', ['ngRoute', 'ngCookies']);

crawlerApp.config(function($routeProvider) {
	$routeProvider

	// route for the home page
	.when('/', {
		templateUrl : './../html/about.html',
	})

	// route for the graph page
	.when('/graph', {
		templateUrl : './../html/graph.html',
		controller  : 'graphController'
	})

	.when('/about', {
		templateUrl : './../html/about.html'//,
	})

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
    	reset: reset,
    	replace: replace
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

	function replace(node, index) {
		graph.nodes[index] = node;
	};
});

crawlerApp.controller('menuController', function($scope, $cookieStore, $http, $location, graphData, $route){
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
		document.getElementById("progress").style.display = "block";

		if(!$scope.data.start || !$scope.data.search || !$scope.data.limit || !Number.isInteger($scope.data.limit)) {
			return;
		}

		var url = "/post";

		$http.post(url, $scope.data)
			.success(function(response, status){
				document.getElementById("error").style.display = "none";
				document.getElementById("progress").style.display = "none";

				graphData.reset();
				if(saveData(response)) {
					addCookie($scope.data);
					$location.path('/graph');
					$route.reload();
				}

				$scope.data = {
					search: "dfs"
				};
			}).
			error(function(data, status){
				document.getElementById("progress").style.display = "none";
				document.getElementById("errorText").innerHTML = "Request failed. Please try again.";
				document.getElementById("error").style.display = "block";
			});
	};

	var saveData = function(text) {
		var parser = new DOMParser();
		var xml = parser.parseFromString(text, 'application/xml');

		var error = xml.getElementsByTagName('error');
		if(error.length > 0) {
			for(var i = 0; i < error[0].children.length; ++i) {
				if(error[0].children[i].nodeName == 'text') {
					document.getElementById("errorText").innerHTML = error[0].children[i].innerHTML;
					document.getElementById("error").style.display = "block";

					return false;
				}
			}
		}

		var pages = xml.getElementsByTagName('page');

		var numPerLevel = {};

		for(var i = 0; i < pages.length; ++i) {
			var nodes = pages[i].children;
			var newNode = {
				keyword: false
			};

			var parent;

			for(var j = 0; j < nodes.length; ++j) {
				if(nodes[j].nodeName == 'parent_id') {
					//graphData.addEdge(nodes[j].id, nodes[j].innerHTML);
					parent = nodes[j].innerHTML;
				}
				else if(nodes[j].nodeName == 'keyword') {
					newNode['keyword'] = true;
					newNode['color'] = {
						background: keywordColor,
						border: "#c60d0d",
						highlight: {
							background: keywordColor,
							border: "#c60d0d"
						},
						hover: {
							border: "#c60d0d",
							background: "#ffaaaa"
						}
					};
				}
				else if(nodes[j].nodeName == 'title') {
					newNode[nodes[j].nodeName] = nodes[j].innerHTML;
					if(nodes[j].innerHTML.length > 10) {
						newNode['label'] = nodes[j].innerHTML.substring(0,7) + "...";
					}
					else {
						newNode['label'] = nodes[j].innerHTML;
					}
				}
				else if(nodes[j].nodeName == 'level') {
					if(nodes[j].innerHTML in numPerLevel) {
						numPerLevel[nodes[j].innerHTML] += 1;
					}
					else {
						numPerLevel[nodes[j].innerHTML] = 1;
					}
					newNode["level"] = nodes[j].innerHTML;
				}
				else {
					newNode[nodes[j].nodeName] = nodes[j].innerHTML;
				}
			}

			graphData.addEdge(parent, newNode["id"]);

			graphData.addNode(newNode);
		}

		var levelRank = {};
		for(var i = 0; i < Object.keys(numPerLevel).length; i++) {
			if (i == 0) {
				levelRank[i] = Math.ceil(numPerLevel[i] / 5);
			}
			else {
				levelRank[i] = Math.ceil(numPerLevel[i] / 5) + levelRank[i-1];
			}
		}

		var nodes = graphData.getGraph().nodes;
		console.log(graphData.getGraph());
		for(var i = 0; i < nodes.length; i++) {
			var newLevel = levelRank[nodes[i]["level"]];
			nodes[i]["level"] = newLevel;
			graphData.replace(nodes[i], i);
		}

		return true;
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

	$scope.about = function(){
		$location.path('/about');
	};
});

// create the controller and inject Angular's $scope
crawlerApp.controller('homeController', function($scope, $cookieStore, $http, $location, graphData) {
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

	$scope.history = function(){
		$location.path('/');
	};
	
	$scope.about = function(){
		$location.path('/about');
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
        	chosen: false,
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
        	hover: true,
        	hoverConnectedEdges: false,
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
		document.getElementById("popupDefault").style.display = "none";
		document.getElementById("popupKeyword").style.display = "none";

		var nodeID = properties.nodes[0];
		console.log("nodeID: " + nodeID);

		if(nodeID) {
			network.focus(nodeID, {
				scale: 1.0,
				animation: true
			}, 500);

			setTimeout(function(){
				for(var i = 0; i < graph.nodes.length; ++i) {
				var node = graph.nodes[i];
				if(node['id'] == nodeID){
				if(node['keyword']) {
					document.getElementById("popupDefault").style.display = "none";
					document.getElementById("kTitle").innerHTML = node['title'];
					document.getElementById("kKeyword").innerHTML = "Contains keyword";
					document.getElementById("kLink").href = node['url'];
					document.getElementById("popupKeyword").style.display = "block";

					var fontSize = 50;
					while(document.getElementById("popupKeyword").clientHeight < document.getElementById("popupKeyword").scrollHeight || document.getElementById("popupKeyword").clientWidth < document.getElementById("popupKeyword").scrollWidth) {
						console.log(fontSize);
						fontSize -= 2;
						document.getElementById("kTitle").style.fontSize = fontSize + "pt";
					}

					console.log(document.getElementById("popupKeyword").clientHeight + ' ' + document.getElementById("popupKeyword").scrollHeight);
				}
				else {
					document.getElementById("popupKeyword").style.display = "none";
					document.getElementById("dTitle").innerHTML = node['title'];
					document.getElementById("dKeyword").innerHTML = "Doesn't contain keyword";
					document.getElementById("dLink").href = node['url'];
					document.getElementById("popupDefault").style.display = "block";

					var fontSize = 50;
					while(document.getElementById("popupDefault").clientHeight < document.getElementById("popupDefault").scrollHeight || document.getElementById("popupDefault").clientWidth < document.getElementById("popupDefault").scrollWidth) {
						console.log(fontSize);
						fontSize -= 2;
						document.getElementById("dTitle").style.fontSize = fontSize + "pt";
					}

					console.log(document.getElementById("popupDefault").clientHeight + ' ' + document.getElementById("popupDefault").scrollHeight);
				}
				}
				}	
			}, 750);
		}
		else {
			document.getElementById('popupKeyword').style.display = "none";
			document.getElementById('popupDefault').style.display = "none";
		}

	});

	network.on('zoom', function(properties){
		document.getElementById('popupKeyword').style.display = "none";
		document.getElementById('popupDefault').style.display = "none";
	});

	network.on('dragStart', function(properties){
		document.getElementById('popupKeyword').style.display = "none";
		document.getElementById('popupDefault').style.display = "none";
	});
});

crawlerApp.controller('historyController', function($scope, $cookieStore, $http, $location, graphData, $route) {
	var historyArr = [];
	var cookieData = $cookieStore.get('graphCrawlerHistoryData');
	var start = cookieData['start'];
	var size = cookieData['size'];
	var cookie = $cookieStore.get('graphCrawlerHistory');

	for(var i = 0; i < size; ++i) {
		var ind = (start+i)%10;
		historyArr.push(cookie[ind]);
	}

	$scope.hist = historyArr.reverse();

	for(var i = 0; i < size; ++i) {
		$scope.hist[i]["id"] = i;
	}

	console.log($scope.hist);

	$scope.view = function(id){
		document.getElementById("progress").style.display = "block";

		var url = "/post";
		console.log($scope.hist[id]);
		$http.post(url, $scope.hist[id])
			.success(function(response, status){
				document.getElementById("error").style.display = "none";
				document.getElementById("progress").style.display = "none";

				graphData.reset();
				saveData(response);

				$location.path('/graph');
				$route.reload();
			}).
			error(function(data, status){
				//error message
				console.log("error");
			});
	};

	$scope.search = function() {
		$location.path('/');
	};

	var saveData = function(text) {
		var parser = new DOMParser();
		var xml = parser.parseFromString(text, 'application/xml');

		var error = xml.getElementsByTagName('error');
		if(error.length > 0) {
			for(var i = 0; i < error[0].children.length; ++i) {
				if(error[0].children[i].nodeName == 'text') {
					document.getElementById("errorText").innerHTML = error[0].children[i].innerHTML;
					document.getElementById("error").style.display = "block";

					return false;
				}
			}
		}

		var pages = xml.getElementsByTagName('page');

		var numPerLevel = {};

		for(var i = 0; i < pages.length; ++i) {
			var nodes = pages[i].children;
			var newNode = {
				keyword: false
			};

			var parent;

			for(var j = 0; j < nodes.length; ++j) {
				if(nodes[j].nodeName == 'parent_id') {
					//graphData.addEdge(nodes[j].id, nodes[j].innerHTML);
					parent = nodes[j].innerHTML;
				}
				else if(nodes[j].nodeName == 'keyword') {
					newNode['keyword'] = true;
					newNode['color'] = {
						background: keywordColor,
						border: "#c60d0d",
						highlight: {
							background: keywordColor,
							border: "#c60d0d"
						},
						hover: {
							border: "#c60d0d",
							background: "#ffaaaa"
						}
					};
				}
				else if(nodes[j].nodeName == 'title') {
					newNode[nodes[j].nodeName] = nodes[j].innerHTML;
					if(nodes[j].innerHTML.length > 10) {
						newNode['label'] = nodes[j].innerHTML.substring(0,7) + "...";
					}
					else {
						newNode['label'] = nodes[j].innerHTML;
					}
				}
				else if(nodes[j].nodeName == 'level') {
					if(nodes[j].innerHTML in numPerLevel) {
						numPerLevel[nodes[j].innerHTML] += 1;
					}
					else {
						numPerLevel[nodes[j].innerHTML] = 1;
					}
					newNode["level"] = nodes[j].innerHTML;
				}
				else {
					newNode[nodes[j].nodeName] = nodes[j].innerHTML;
				}
			}

			graphData.addEdge(parent, newNode["id"]);

			graphData.addNode(newNode);
		}

		var levelRank = {};
		for(var i = 0; i < Object.keys(numPerLevel).length; i++) {
			if (i == 0) {
				levelRank[i] = Math.ceil(numPerLevel[i] / 5);
			}
			else {
				levelRank[i] = Math.ceil(numPerLevel[i] / 5) + levelRank[i-1];
			}
		}

		var nodes = graphData.getGraph().nodes;
		console.log(graphData.getGraph());
		for(var i = 0; i < nodes.length; i++) {
			var newLevel = levelRank[nodes[i]["level"]];
			nodes[i]["level"] = newLevel;
			graphData.replace(nodes[i], i);
		}

		return true;
	};
});












































