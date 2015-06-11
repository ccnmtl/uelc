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
        var envelope = JSON.parse(evt.data);
        var data = JSON.parse(envelope.content);
        var groupId = data.userId; //data["user_id"];
        var sectionId = data.sectionPk; //["section_pk"];
        var notificationType = data.notification; //["notification"];
        var groupColumnSelector = '#group-user-section-' + groupId;
        window.sectionRowSelector = '[data-section-id="' + String(sectionId) + '"]';
        window.sectionBlock = jQuery(groupColumnSelector + ' ' + sectionRowSelector);
        //var gateBtn = getTheBtn.find('.gate-button');

        if(data.notification == "At Gate Block"){
            var msg = 'we just landed on a page with a gateblock!';
            updateGateSectionStatus(groupColumnSelector, sectionBlock)
            setGroupLocation(groupColumnSelector, sectionBlock)
            //highlightActiveGate(groupColumnSelector, sectionBlock)
            //setGroupMessage(jQuery(groupColumnSelector), msg);
        }
        if(data.notification == "Decision Submitted"){
            var msg = 'we just made a decision';
            setGroupMessage(jQuery(groupColumnSelector), msg);   
        }

        

        /*if (gateBtn.hasClass('locked')) { //console.log("This button is locked");
            gateBtn.removeClass('locked').addClass('unlocked');
            gateBtn.find('.btn-group-vertical > button.btn-sm')
            .removeClass('btn-incomplete')
            .addClass('btn-waiting');
            //need to remove input elements... maybe move form tag and remove that
        }
        */
        //need to change button to success when user clicks to unlock the gate
    };

    if (window.WebSocket) {
        connectSocket();
    } else {
        alert($('Your browser does not support WebSockets. ' +
                'You will have to refresh your browser to view updates.'));
    }
    var setGroupLocation = function(groupColumnSelector, sectionBlock){
        var groupIcon = jQuery('<span class="glyphicon glyphicon-user" aria-hidden="true"></span>');
        jQuery(groupColumnSelector).find('.glyphicon-user').remove();
        sectionBlock.find('.gate-button').prepend(groupIcon);
    }

    var updateGateSectionStatus = function(groupColumnSelector, sectionBlock){
        var badge = sectionBlock.find('.badge');
        if(badge.text() == 'reviewed'){
            return
        }else{
            badge.text('reviewing')
        }
    }

    var highlightActiveGate = function(groupColumnSelector, sectionBlock){
        jQuery(groupColumnSelector).find('.gate-block').each(function(){
            jQuery(this).removeClass('active');
        });
        sectionBlock.addClass('active');
    }

    var setGroupMessage = function(groupColumn, msg){
        msgHtml = jQuery('<div class="group-message alert alert-warning alert-dismissable">' +
                         '<button type="button" class="close" data-dismiss="alert"' + 
                         'aria-hidden="true">×</button></div>');
        msgHtml.append(msg);
        groupColumn.prepend(msgHtml);
    }
});
