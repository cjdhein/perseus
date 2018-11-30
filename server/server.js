// Load required modules
const express = require("express");
const fs = require("fs");
const bodyParser = require("body-parser");
const shortid = require("shortid");
const execFile = require("child_process").execFile;

// Define constants
const PORT = 3005;
const DFS_LIMIT = 100; // page limit for breadth-first search
const BFS_LIMIT = 3; // page limit for depth-first search
const DFS_SEARCH = 1; // DO NOT EDIT - search value sent to python web crawler for dfs
const BFS_SEARCH = 2; // DO NOT EDIT - search value sent to python web crawler for bfs
const PATH_LOGS = "/public/log_files/"; // Path where log files are stored
const CWD_CRAWLER = "../crawler"; // Path to python script
const PYTHON_SCRIPT_NAME = "core.py";
const TIMEOUT = 60000; // kill child process after this many milliseconds
const SIGNAL = "SIGTERM"; // signal to send to terminate child process

// ERR_TEXT is the text of the error log file sent by send_error_xml_response
const ERR_TEXT = [
	"The required values were not sent to the server. Please try again.", //0
	"The numeric limit is too high for this search method. Please enter a lower numeric limit and try again.", //1
	"Timeout: The data crawler did not complete execution in time. Please try a different search.", //2
	"There was an error with the data crawler. Please try a different search." //3
];

// Initialize Express
var app = express();
app.use(bodyParser.urlencoded({extended:false}));
app.use(bodyParser.json());
app.set("port", PORT);
app.use(express.static("public"));

app.use(express.static(PATH_LOGS));


// Homepage
// Receive a GET request, send HTML response
app.get("/", function(req, res) {
	res.status(200);
	res.sendFile(__dirname + "/public/html/index.html");
});


// POST request
// Receive a POST request, handle form data, send XML response
app.post("/post", function(req, res) {

	/* Handle form data */

	// Form data is stored as an array (not an object) to preserve order
	var form_data = [
		{key: "start", val: null},
		{key: "search", val: null},
		{key: "limit", val: null},
		{key: "keyword", val: null}
	];

	// For each key: Validate that the value submitted by the form is valid
	//               Put the associated value in the form_data array
	for (var i = 0; i < form_data.length; i++) {
		var key = form_data[i].key; // key from the form_data array
		var val = req.body[key];	// val submitted by the form
		
		// Check that all required parameters exist
		if (key != "keyword") { // "keyword" is not required
			// If required parameter is missing, send error XML file
			if (val == "" || val == undefined || val == null) {
				send_error_xml_response(res, 0);
				return; // Stop execution so another response is not returned
			}
		}

		// Check that "search" has value "dfs" or "bfs"
		if (key == "search") {

			// Convert "dfs" or "bfs" received from web page
			// into DFS_SEARCH or BFS_SEARCH to send to web crawler
			if (val == "dfs") {
				val = DFS_SEARCH;
			} else if (val == "bfs") {
				val = BFS_SEARCH;

			// If "search" is not a valid value, send an error response
			} else {
				send_error_xml_response(res, 0);
				return; // Stop execution so another response is not returned
			}
		}

		// Check that "limit" is within allowable ranges
		if (key == "limit") {

			// Ensure valid "limit" for breadth-first search
			if (form_data[1].val == BFS_SEARCH) {
				if (val < 1 || val > BFS_LIMIT) {
					send_error_xml_response(res, 1);
					return; // Stop execution so another response is not returned
				}
			}
			
			// Ensure valid "limit" for depth-first search
			if (form_data[1].val == DFS_SEARCH) {
				if (val < 1 || val > DFS_LIMIT) {
					send_error_xml_response(res, 1);
					return; // Stop execution so another response is not returned
				}
			}
		}

		// If "keyword" does not exist (undefined or null), set value to empty string
		if (key == "keyword") {
			if (val == undefined || val == null) {
				val = "";
			}
		}

		form_data[i].val = val;
	} //end for loop over form_data


	/* Create filename to send to data crawler */
	var filename = generate_filename();


	/* Call the Data Crawler (Python script) */
	// Reference: https://stackoverflow.com/questions/23450534/how-to-call-a-python-function-from-node-js
	// Reference: https://nodejs.org/api/child_process.html
	var pythonProcess;

	// If keyword (form_data[3].val) does not exists, call data crawler without keyword
	if (form_data[3].val == "") {
		pythonProcess = execFile('pipenv',
			['run','python3',PYTHON_SCRIPT_NAME, filename,
			form_data[0].val, form_data[2].val, form_data[1].val],
			{cwd:CWD_CRAWLER, timeout:TIMEOUT, killSignal:SIGNAL},
			// Callback function
			function (error, stdout, stderr) {
				if (stderr) {console.error(stderr)}; // print stderr from child process
				if (error) {
					console.error(error);
					send_error_xml_response(res, 2);
					return; // Stop execution so another response is not returned
				}
				send_response(res, filename);
			}
		);
	}
	// Else keyword exists, call data crawler with keyword
	else {
		pythonProcess = execFile('pipenv',
			['run','python3',PYTHON_SCRIPT_NAME, filename,
			form_data[0].val, form_data[2].val, form_data[1].val, form_data[3].val],
			{cwd:CWD_CRAWLER, timeout:TIMEOUT, killSignal:SIGNAL},
			// Callback function
			function (error, stdout, stderr) {
				if (stderr) {console.error(stderr)}; // print stderr from child process
				if (error) {
					console.error(error);
					send_error_xml_response(res, 2);
					return; // Stop execution so another response is not returned
				}
				send_response(res, filename);
			}
		);
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


// Start the Express server
app.listen(app.get("port"), function() {
	console.log("Express started on http://localhost:" + app.get("port") + "; press Ctrl-C to terminate.");
});



/* This function sends an XML response with the text associated with err_number
 * @param {Object} res - Express response object
 * @param {number} err_number - Numeric error code associated with array ERR_TEXT
 */
function send_error_xml_response(res, err_number) {
	var response_body = "<?xml version='1.0' ?><crawler_log><error><code>"
	response_body += err_number;
	response_body += "</code><text>";
	response_body += ERR_TEXT[err_number];
	response_body += "</text></error></crawler_log>"

	res.type("application/xml");
	res.status(200);
	res.send(response_body);
}



/* This function creates a random filename prepended by "log_"
 * @return {string} filename - randomly generated filename
 */
function generate_filename() {
	var id = shortid.generate();
	var filename = "crawler_log_" + id + ".xml";
	return filename;
}


/* This is the callback function for the python web crawler
 * This function sends the contents of the log file back to the web page
 *
 */
function send_response(res, filename) {
	try {
		if (fs.existsSync(__dirname + PATH_LOGS + filename)) {
			res.type("application/xml");
			res.status(200);
			res.sendFile(__dirname + PATH_LOGS + filename);
			return;
		} else {
			send_error_xml_response(res, 3);
			return;
		}
	} catch(err) {
		console.error(err)
		send_error_xml_response(res, 3);
		return;
	}
}
