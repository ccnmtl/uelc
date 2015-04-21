$(function() {
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
	            console.log("UpdateToken Error");
	        },
	        success: function(d) {
	            window.token = d.token;
	            console.log("UpdateToken Success!");
	        }
	    });
	};
	
	
	var connectSocket = function() {
        conn = new WebSocket(window.websockets_base + "?token=" + window.token);
        //conn.onclose = requestFailed;
        //conn.onmessage = onMessage;
        conn.onopen = function (evt) {
            currentRefresh = defaultRefresh;
            alert("connectSocket() connected!");
            //appendLog($("<div class='alert alert-info'><b>Connected to server.</b></div>"));
        };
    };


	console.log("window.websockets_base");
	console.log(window.websockets_base);
	console.log("window.token");
	console.log(window.token);
	console.log("window.username");
	console.log(window.username);
	console.log("window.fresh_token_url");
	console.log(window.fresh_token_url);
	
	
    if (window.WebSocket) {
        connectSocket();
    } else {
        alert($("Your browser does not support WebSockets. You will have to refresh your browser to view updates."));
    }
});