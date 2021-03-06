$(function() {

    // Taken from Tala
    var currentRefresh = 1000;
    var defaultRefresh = 1000;
    var maxRefresh = 1000 * 5 * 60; // 5 minutes

    var updateToken = function() {
        $.ajax({
            url: window.freshTokenUrl,
            type: 'get',
            dateType: 'json',
            error: function(evt) {
                // eslint-disable-next-line scanjs-rules/call_setTimeout
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
        // eslint-disable-next-line scanjs-rules/call_setTimeout
        setTimeout(connectSocket, currentRefresh);
    };

    var connectSocket = function() {
        var conn = new WebSocket(
            window.websocketsBase + '?token=' + window.token);
        conn.onclose = requestFailed;
        conn.onmessage = onMessage;
        conn.onopen = function(evt) {
            currentRefresh = defaultRefresh;
        };
        $(window).on('beforeunload', function() {
            conn.close();
        });
    };

    var onMessage = function(evt) {
        var envelope = JSON.parse(evt.data);
        var data = JSON.parse(envelope.content);
        if (data.notification === 'Open Gate') {
            if ((data.section === parseInt(window.sectionId)) &&
            (data.username === window.username)) {
                jQuery('ul.pager li.next a').removeClass('disabled');
                jQuery('ul.pager li.next a').css('color', '#337ab7');
                jQuery('ul.pager li.next a').attr('href', data.nextUrl);
                jQuery('.wait-msg').hide();
                jQuery('.unlock-msg').show();
            }
        }
    };

    if (window.WebSocket) {
        connectSocket();
    } else {
        alert($('Your browser does not support WebSockets. ' +
                'You will have to refresh your browser to view updates.'));
    }
});
