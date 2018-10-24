
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
    	getGraph: get
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
});

// create the controller and inject Angular's $scope
crawlerApp.controller('homeController', function($scope, $cookieStore, $http, $location, graphData) {
	//TODO: Send request to server to retrieve graph from search terms
	//$scope.submit = function(){
	//var url = ;
	// var data = {
	// 	start: ,
	// 	search: ,
	// 	limit: ,
	// 	keyword: ,
	// };
	// $http.post(url, data).then(function(response){
	// 	if(success){
	// 		parse data and save to graphData
	// 		save cookie
	// 		$location.path('/graph');
	// 	}
	// 	else{
	// 		show error
	// 	}
	// });
	//}

	//TODO: After receiving request, parse data and update graph service
	var text = `<data>
	<page>
	<id>0</id>
	<title>Google</title>
	<url>https://www.google.com/</url>
</page>
<page>
	<id>1</id>
	<title>Google</title>
	<url>https://www.google.com/</url>
	<parent_id>0</parent_id>
	<keyword />
</page>
</data>`;

	var parser = new DOMParser();
	var xml = parser.parseFromString(text, 'application/xml');
	var pages = xml.getElementsByTagName('page');

	for(var i = 0; i < pages.length; ++i) {
		var nodes = pages[i].children;
		var newNode = {
			keyword: false
		};
		for(var j = 0; j < nodes.length; ++j) {
			if(nodes[j].nodeName == 'parent_id') {
				graphData.addEdge(i, nodes[j].innerHTML);
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

	console.log(graphData.getGraph());

	$scope.history = function(){
		$location.path('history');
	};

});

crawlerApp.controller('graphController', function($scope, graphData) {
	//TODO: Create node and edges from graph service
	//var graph = graphData.getGraph();
	//var nodes = new vis.DataSet(graph.nodes);
	//var edges = new vis.DataSet(graph.edges);

	var nodes = new vis.DataSet([
    	{id: 1, label: 'Node 1', url: 'www.google.com'},
    	{id: 2, label: 'Node 2'},
    	{id: 3, label: 'Node 3'},
    	{id: 4, label: 'Node 4'},
    	{id: 5, label: 'Node 5'}
	]);

	// create an array with edges
	var edges = new vis.DataSet([
    	{from: 1, to: 3},
    	{from: 1, to: 2},
    	{from: 2, to: 4},
    	{from: 2, to: 5}
	]);

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
		var nodeID = properties.nodes[0];

		if(nodeID) {
			setTimeout(function(){
				document.getElementById("popup").style.display = "block";
				//document.getElementById("pTitle").innerHTML = nodeID['title'];
				//document.getElementById("pInfo").innerHTML = nodeID['info'];
				//document.getElementById("pLink").href = nodeID['link'];

				network.focus(nodeID, {
					scale: 1.0,
					animation: true
				}, 1000);
			});
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
	//TODO: Update scope with history cookie
	$scope.hist = [{
		id: 1,
		start: "www.google.com",
		search: "dfs",
		limit: 1,
		keyword: ""
	},
	{
		id: 2,
		start: "www.google.com",
		search: "bfs",
		limit: 2,
		keyword: "asdf"
	},
	{
		id: 3,
		start: "www.google.com",
		search: "dfs",
		limit: 3,
		keyword: "a"
	},
	{
		id: 4,
		start: "www.google.com",
		search: "bfs",
		limit: 4,
		keyword: "b"
	},
	{
		id: 5,
		start: "www.google.com",
		search: "dfs",
		limit: 5,
		keyword: "c"
	},
	{
		id: 1,
		start: "www.google.com",
		search: "dfs",
		limit: 1,
		keyword: ""
	},
	{
		id: 2,
		start: "www.google.com",
		search: "bfs",
		limit: 2,
		keyword: "asdf"
	},
	{
		id: 3,
		start: "www.google.com",
		search: "dfs",
		limit: 3,
		keyword: "a"
	},
	{
		id: 4,
		start: "www.google.com",
		search: "bfs",
		limit: 4,
		keyword: "b"
	},
	{
		id: 5,
		start: "www.google.com",
		search: "dfs",
		limit: 5,
		keyword: "c"
	},
	];

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












































