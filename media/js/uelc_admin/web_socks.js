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
	            console.log("UpdateToken Error");
	        },
	        success: function(d) {
	            window.token = d.token;
	            console.log("UpdateToken Success!");
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
        //conn.onclose = requestFailed;
        //conn.onmessage = onMessage;
        conn.onopen = function (evt) {
            currentRefresh = defaultRefresh;
            alert("connectSocket() connected!");
        };
    };


    var onMessage = function (evt) {
        var envelope = JSON.parse(evt.data);
        var data = JSON.parse(envelope.content);
        
        console.log("envelope");
    	console.log(envelope);
    	console.log("data");
    	console.log(data);


    	

//        var entry = $("<div/>");
//        entry.addClass("row");
//        var d = new Date();
//        var hours = d.getHours();
//        var minutes = d.getMinutes();
//
//        if (minutes < 10) {
//            minutes = "0" + minutes;
//        }
//        entry.append("<div class='span1 timestamp'>" + hours + ":" + minutes + "</div>");
//        entry.append("<div class='span2 nick'>&lt;" + data.username + "&gt;</div>");
//        entry.append("<div class='span5 ircmessage'>" + data.message_text + "</div>");
//        appendLog(entry);
//        MathJax.Hub.Queue(["Typeset",MathJax.Hub, entry[0]]);
    };
	
	
    if (window.WebSocket) {
        connectSocket();
    } else {
        alert($("Your browser does not support WebSockets. You will have to refresh your browser to view updates."));
    }
});