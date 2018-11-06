const express = require("express");
const fs = require("fs");
const bodyParser = require("body-parser");

var app = express();
app.use(bodyParser.urlencoded({extended:false}));
app.use(bodyParser.json());

var path = "/public/log_files/"; //Path where log files are stored

app.set("port", 3540);
app.use(express.static("public"));

// Homepage
app.get("/", function(req, res) {
	res.sendFile(__dirname + "/public/html/index.html");
});

// POST request
app.post("/post", function(req, res) {

	// Deal with req data here, call data crawler
	for (var param in req.body) {
		console.log("Param: " + param + ", Value: " + req.body[param]);
	}



	var filename = "log_example_5.xml";

	try {
		if (fs.existsSync(__dirname + path + filename)) {
			
			console.log(filename + " exists."); //for testing

			res.type("application/xml");
			res.sendFile(__dirname + path + filename);

		} else {
			console.log(filename + " does not exist."); //for testing
		}
	} catch(err) {
		console.error(err)
	}

	
	//For testing:
	//res.send("<?xml version=\"1.0\" ?><page>Post successfully received.</page>")
});

// 404
app.use(function(req, res) {
	res.type("text/plain");
	res.status(404);
	res.send("404 - Not Found");
});

// 500
app.use(function(err, req, res, next) {
	console.error(err.stack);
	res.type("text/plain");
	res.status(500);
	res.send("500 - Server Error");
});

app.listen(app.get("port"), function() {
	console.log("Express started on http://localhost:" + app.get("port") + "; press Ctrl-C to terminate.");
});
