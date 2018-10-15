document.getElementById("form").addEventListener("submit", function (event) {
	//Commented out code to send a POST request to the server. This will be implemented next.
	/*
	var req = new XMLHttpRequest();
	payload = {
		"createEntry": "createEntry",
		url: document.getElementById("url").value,
		breadth: document.getElementById("breadth").checked, //true for breadth, false for depth
		limit: document.getElementById("limit").value,
		keyword: document.getElementById("keyword").value,
	};
	req.open("POST", "/", true);
	req.setRequestHeader("Content-Type", "application/json");
	req.addEventListener("load", function() {
		var response = req.responseText;
		
		// Call function to display graphics

	});
	req.send(JSON.stringify(payload));
	event.preventDefault();
	*/

	var textNode = document.createTextNode("Button clicked. ");
	document.body.appendChild(textNode);
	event.preventDefault();
});
