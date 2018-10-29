/* Override the event handler for the form "Submit" button.
*  Send an asynchronous POST request to the server.
*/
document.getElementById("form").addEventListener("submit", function (event) {
	sendPost();
	event.preventDefault();
});


/* Send the form data to the server via HTTP POST.
*  Asynchronously receive a response from the server.
*/
function sendPost() {
	var req = new XMLHttpRequest();
	payload = {
		url: document.getElementById("url").value,
		breadth: document.getElementById("breadth").checked, //true for breadth, false for depth
		limit: document.getElementById("limit").value,
		keyword: document.getElementById("keyword").value,
	};
	req.open("POST", "/post", true);
	req.setRequestHeader("Content-Type", "application/json");

	// Executes upon asynchronous response from server
	req.addEventListener("load", function() {
		var response = req.responseText;
		displayGraphics(response);
	});

	req.send(JSON.stringify(payload));
}


/* This function takes the XML response from the server and generates a graph.
*  param: response (XML-formatted)
*/
function displayGraphics(response) {
	// The following two lines are for testing, and can be commented out:
	var textNode = document.createTextNode(response + " ");
	document.body.appendChild(textNode);

	// Add code here to display the XML response
}
