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
        $(window).on('beforeunload', function() {
            conn.close();
        });
    };

    var onMessage = function(evt) {
        var msg;
        var action;
        var envelope = JSON.parse(evt.data);
        var data = JSON.parse(envelope.content);
        var groupId = data.userId; //data["user_id"];
        var sectionId = data.sectionPk; //["section_pk"];
        var notificationType = data.notification; //["notification"];
        var groupColumnSelector = '#group-user-section-' + groupId;
        var sectionRowSelector = '[data-section-id="' +
            String(sectionId) + '"]';
        var sectionBlock = jQuery(groupColumnSelector + ' ' +
            sectionRowSelector);

        if (data.notification.message === 'At Gate Block') {
            msg = 'we just landed on a page with a gateblock!';
            action = 'gateblock';
            setGroupLocation(groupColumnSelector, sectionBlock);
            updateGateSectionStatus(groupColumnSelector, sectionBlock, action);
        }
        if (data.notification.message === 'Section Submitted') {
            msg = 'we just confirmed a page';
            action = 'section submitted';
            updateGateSectionStatus(groupColumnSelector, sectionBlock, action);
            setGroupLocation(groupColumnSelector, sectionBlock);
            highlightActiveGate(groupColumnSelector, sectionBlock);
            setGroupMessage(jQuery(groupColumnSelector), msg);
            UA.setFormClickHandler();
        }
        if (data.notification.message === 'Decision Submitted' &&
            data.notification.data !== null
           ) {
            msg = 'we just made a decision';
            action = 'made decision';
            setGroupMessage(jQuery(groupColumnSelector), msg);
            updateGateSectionStatus(groupColumnSelector, sectionBlock, action);
            highlightActiveGate(groupColumnSelector, sectionBlock);
            displayDecisionTitle(groupColumnSelector, sectionBlock, data);
            UA.setFormClickHandler();
            UA.setCurveballCommitAccess();
        }
        if (data.notification.message === 'Open Gate') {
            openGate(groupColumnSelector, sectionBlock);
        }
    };

    if (window.WebSocket) {
        connectSocket();
    }else {
        alert($('Your browser does not support WebSockets. ' +
                'You will have to refresh your browser to view updates.'));
    }
    var displayDecisionTitle = function(gcs, sectionBlock, data) {
        var gateSection = sectionBlock.find('.gate-section');
        gateSection.append('<div class-"response">' +
            data.notification.data + '</div>');
    };
    var setGroupLocation = function(gcs, sectionBlock) {
        var groupIcon = jQuery('<span class="glyphicon glyphicon-user ' +
            ' pull-right" aria-hidden="true"></span>');
        jQuery(gcs).find('.glyphicon-user').remove();
        sectionBlock.find('.gate-section .panel-body').prepend(groupIcon);
        // Look for this column's corresponding .group-name box, and
        // hide the user icon in case it's there.
        sectionBlock.closest('.col-sm-3').find(
            '.group-name .user-icon').hide();
    };
    var openGate = function(groupColumnSelector, sectionBlock) {
        var btn = sectionBlock.find('.btn-danger');
        var glyph = sectionBlock.find('.glyphicon-lock');
        jQuery(groupColumnSelector).find('.gate-block').each(function() {
            jQuery(this).removeClass('active');
        });

        btn.removeClass('btn-danger').addClass('btn-success');
        glyph.removeClass('glyphicon-lock').addClass('glyphicon-ok');
    };
    var updateGateSectionStatus = function(gcs, sectionBlock, action) {
        var badge = sectionBlock.find('.badge');
        if (action === 'section submitted' || action === 'made decision') {
            badge.text('reviewed');
            badge.removeClass('reviewing').addClass('reviewed');
            return;
        }
        if (badge.text() === 'reviewed') {
            return;
        }else {
            badge.text('reviewing');
            badge.removeClass('to be reviewed');
            badge.addClass('reviewing');
        }
    };

    var highlightActiveGate = function(groupColumnSelector, sectionBlock) {
        jQuery(groupColumnSelector).find('.gate-block').each(function() {
            jQuery(this).removeClass('active');
        });
        sectionBlock.addClass('active');
    };

    var setGroupMessage = function(groupColumn, msg) {
        var groupNameDiv =  groupColumn.find('.group-name');
        var msgHtml = jQuery('<div class="group-message alert alert-warning ' +
            'alert-dismissable">' +
            '<button type="button" class="close" data-dismiss="alert"' +
            'aria-hidden="true">×</button></div>');
        msgHtml.append(msg);
        groupNameDiv.append(msgHtml);
    };
});
