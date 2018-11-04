const express = require("express");
const fs = require("fs");
const bodyParser = require("body-parser");
//const spawn = require("child_process").spawn;

const BFS_LIMIT = 5; // page limit for breadth-first search
const DFS_LIMIT = 8; // page limit for depth-first search

var app = express();
app.use(bodyParser.urlencoded({extended:false}));
app.use(bodyParser.json());

var path_logs = "/public/log_files/"; // Path where log files are stored
var path_python_crawler = "/public/python/webcrawler.py"; // Path to python script

app.set("port", 3000);
app.use(express.static("public"));

// Homepage
app.get("/", function(req, res) {
	res.status(200);
	res.sendFile(__dirname + "/public/html/index.html");
});

// POST request
app.post("/post", function(req, res) {

	/* Handle form data */

	var request_params = ["start", "search", "limit", "keyword"];
	var request_values = []; //stores value associated with each request_params

	// For each request_params, put the associated form data in request_values
	for (var i = 0; i < request_params.length; i++) {
		var param = request_params[i];
		var value = req.body[param];
		
		// Check that all required parameters exist
		if (param != "keyword") { // "keyword" is not required
			// If required parameter is missing, send error XML file
			if (value == "" || value == undefined || value == null) {
				send_error_xml_response(res, 3, "Error: missing required parameter: " + param);
				return; // Stop execution so another response is not returned
			}
		}

		// Check that "search" has value "dfs" or "bfs"
		if (param == "search") {
			if (value != "dfs" && value != "bfs") {
				send_error_xml_response(res, 4, "Error: invalid value for parameter: " + param);
				return; // Stop execution so another response is not returned
			}
		}
/*
		// Check that "limit" is a positive integer
		if (param == "limit") {
			if (Number(value) <= 0 || Number.isInteger(value) == false) {
				send_error_xml_response(res, 6, "Error: invalid value for parameter: " + param);
				return; // Stop execution so another response is not returned
			}
		}
*/

		// Check that limit is within allowable ranges
		if (param == "limit") {

			// Ensure valid limit for breadth-first search
			if (request_values[1] == "bfs") {
				if (value < 1 || value > BFS_LIMIT) {
					send_error_xml_response(res, 2, "Page limit too high");
					return; // Stop execution so another response is not returned
				}
			}
			
			// Ensure valid limit for depth-first search
			if (request_values[1] == "dfs") {
				if (value < 1 || value > DFS_LIMIT) {
					send_error_xml_response(res, 2, "Page limit too high");
					return; // Stop execution so another response is not returned
				}
			}
		}


		// If keyword does not exist (undefined or null), set value to empty string
		if (param == "keyword") {
			if (value == undefined || value == null) {
				value = "";
			}
		}

		request_values[i] = value;
	} //end for loop over request_params



	/* Call the Data Crawler (Python script) */

	// Reference: https://stackoverflow.com/questions/23450534/how-to-call-a-python-function-from-node-js

/*	
	const pythonProcess = spawn('python',["path/to/script.py", arg1, arg2, ...]);

	//modified version:
	const pythonProcess = spawn('python', [path_python_crawler,
		request_values[0], request_values[1], request_values[2], request_values[3]);

	pythonProcess.stdout.on('data', (data) => {
		// Do something with the data returned from python script
	});
*/




	var filename = "log_example_5.xml";

	try {
		if (fs.existsSync(__dirname + path_logs + filename)) {
			res.type("application/xml");
			res.status(200);
			res.sendFile(__dirname + path_logs + filename);
		} else {
			send_error_xml_response(res, 0, "File does not exist");
		}
	} catch(err) {
		console.error(err)
	}
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



/* This function sends an XML response with a given error code, error text
 * @param {Object} res - Express response object
 * @param {number} code - Numeric error code
 * @param {string} text - Error text
 */
function send_error_xml_response(res, code, text) {
	var response_body = "<?xml version='1.0' ?><crawler_log><error><code>"
	response_body += code;
	response_body += "</code><text>";
	response_body += text;
	response_body += "</text></error></crawler_log>"

	res.type("application/xml");
	res.status(200);
	res.send(response_body);
}
