$(function() {

    // Taken from Tala
    var conn;
    var currentRefresh = 1000;
    var defaultRefresh = 1000;
    var maxRefresh = 1000 * 5 * 60; // 5 minutes

    var updateToken = function() {
        $.ajax({
            url: window.freshTokenUrl,
            type: 'get',
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
        setTimeout(connectSocket, currentRefresh);
    };

    var connectSocket = function() {
        conn = new WebSocket(window.websocketsBase + '?token=' + window.token);
        conn.onclose = requestFailed;
        conn.onmessage = onMessage;
        conn.onopen = function(evt) {
            currentRefresh = defaultRefresh;
        };
    };

    var onMessage = function(evt) {
        //console.log("onMessage");
        var envelope = JSON.parse(evt.data);
        var data = JSON.parse(envelope.content);

        //console.log("data");
        //console.log(data);
        var groupId = data.userId; //data["user_id"];
        var sectionId = data.sectionPk; //["section_pk"];
        var notificationType = data.notification; //["notification"];
        //console.log("notification_type");
        //console.log(notification_type);
        var groupColumn = '[data-group-id="' + String(groupId) + '"]';
        var sectionRow = '[data-section-id="' + String(sectionId) + '"]';

        var getTheBtn = jQuery(groupColumn + sectionRow);

        var gateBtn = getTheBtn.find('.gate-button');

        if (gateBtn.hasClass('locked')) { //console.log("This button is locked");
            gateBtn.removeClass('locked').addClass('unlocked');
            gateBtn.find('.btn-group-vertical > button.btn-sm')
            .removeClass('btn-incomplete')
            .addClass('btn-waiting');
            //need to remove input elements... maybe move form tag and remove that
        }
        //need to change button to success when user clicks to unlock the gate
    };

    if (window.WebSocket) {
        connectSocket();
    } else {
        alert($('Your browser does not support WebSockets. ' +
                'You will have to refresh your browser to view updates.'));
    }
});
