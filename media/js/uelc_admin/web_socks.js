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
        conn.onclose = requestFailed;
        conn.onmessage = onMessage;
        conn.onopen = function (evt) {
            currentRefresh = defaultRefresh;
            console.log("connectSocket() connected!");
        };
    };


    var onMessage = function (evt) {
    	//console.log("onMessage");
        var envelope = JSON.parse(evt.data);
        var data = JSON.parse(envelope.content);
        
    	//console.log("data");
    	//console.log(data);
    	var group_id = data["user_id"];

    	var section_id = data["section_pk"];
    	var group_column = "[data-group-id='" + String(group_id) + "']";
    	var section_row = "[data-section-id='" + String(section_id) + "']";
    	
    	var get_the_btn = jQuery(group_column + section_row);
    	
        var gate_btn = get_the_btn.find('.gate-button');

    	if(gate_btn.hasClass('locked'))
    	{ //console.log("This button is locked"); 
    	  gate_btn.removeClass('locked').addClass('unlocked');
    	  gate_btn.find('.btn-group-vertical > button.btn-sm').removeClass('btn-incomplete').addClass('btn-waiting');
    	  //need to remove input elements... maybe move form tag and remove that
    	}
    	//need to change button to success when user clicks to unlock the gate
    };
	
	
    if (window.WebSocket) {
        connectSocket();
    } else {
        alert($("Your browser does not support WebSockets. You will have to refresh your browser to view updates."));
    }
});