$(function() {
	
	// Taken from Tala
	var conn;
	var currentRefresh = 1000;
	var defaultRefresh = 1000;
	var maxRefresh = 1000 * 5 * 60; // 5 minutes
	
	var updateToken = function() {
	    $.ajax({
	        url: window.fresh_token_url,
	        type: "get",
	        dateType: 'json',
	        error: function(evt) {
	            setTimeout(updateToken, currentRefresh);
	        },
	        success: function(d) {
	            window.token = d.token;
	        }
	    });
	};
	
	var requestFailed = function(evt) {
        // circuit breaker pattern for failed requests
        // to ease up on the server when it's having trouble
        updateToken();
        currentRefresh = 2 * currentRefresh; // double the refresh time
        if (currentRefresh > maxRefresh) {
            currentRefresh = maxRefresh;
        }
        setTimeout(connectSocket,currentRefresh);
    };
	
	var connectSocket = function() {
        conn = new WebSocket(window.websockets_base + "?token=" + window.token);
        conn.onclose = requestFailed;
        conn.onmessage = onMessage;
        conn.onopen = function (evt) {
            currentRefresh = defaultRefresh;
        };
    };

    var onMessage = function (evt) {
        var envelope = JSON.parse(evt.data);
        var data = JSON.parse(envelope.content);
        
    	console.log("data");
    	console.log(data);

    	// { hierarchy: "case-one", notification: "Open Gate", section: 69, user_id: 52 }
    	if (data['section'] === window.section_id)
    	{
    		console.log("data section id matches current section id");
    	}
    	if (data['username'] === window.user_id)
    	{
    		console.log("data user id matches current user id");
    	}
    	
    };
	
	
    if (window.WebSocket) {
        connectSocket();
    } else {
        alert($("Your browser does not support WebSockets. You will have to refresh your browser to view updates."));
    }
});