var UELCAdmin;
UELCAdmin = {
    Admin: function() {
        this.init = function() {
            this.setFormClickHandler();
            this.separateParts();
            this.setCurveballCommitAccess();

            jQuery('form[name="curveball-form-select"]').submit(
                    this.confirmCurveball);
            jQuery('#confirm-curveball-modal .set-curveball').click(
                    this.setCurveball);
            jQuery('#confirm-curveball-modal .cancel-curveball').click(
                    this.cancelCurveball);
        };
        this.setChoicesOnParts = function() {
            jQuery('.user-part2').each(function() {
                var partTwoHeader = jQuery('<div class="part2-header">' +
                    'Part 2</div>');
                var header = jQuery(this);
                window.hed = header;
                var col = header.parent().children('.gate-section-list').eq(0);
                var rt = col.find('.response').eq(1).text();
                jQuery(this).prepend(partTwoHeader);
                partTwoHeader.append(rt);
            });
        };
        this.separateParts = function() {
            jQuery('.gate-section-list').each(function() {
                var partTwo = jQuery(this).children('.part-2');
                var wrapDiv = '<div class="gate-section-list well well-sm ' +
                'user-part2"></div>';
                var glyph = '<span class="glyphicon ' +
                'glyphicon-triangle-bottom" aria-hidden="true"></span>';
                partTwo.detach().wrapAll(wrapDiv).parent().insertAfter(this);
                jQuery(this).after(glyph);
            });
            this.setChoicesOnParts();
        };
        this.setCurveballCommitAccess = function() {
            jQuery('.curveball-commit-btn').each(function() {
                var $btn = jQuery(this);
                var $thisGate = $btn.closest('.gate-block');
                var $prevGate = $thisGate.prev();
                if ($prevGate.find('.badge').text() !== 'reviewed') {
                    $btn.attr('disabled', 'disabled');
                } else {
                    $btn.removeAttr('disabled');
                }
            });
        };
        this.confirmCurveball = function(evt) {
            evt.preventDefault();
            var frm = evt.currentTarget;
            var $thisGate = jQuery(this).closest('.gate-block');
            var $prevGate = $thisGate.prev();

            window.UA.curveballData = jQuery(frm).serialize() + '&' +
                $prevGate.find('.gate-button form').serialize();

            var $modal = jQuery('#confirm-curveball-modal');
            $modal.find('.instructions').html(
                'Are you sure? This cannot be undone');
            $modal.find('.loading-spinner').addClass('hidden');
            $modal.modal('show');
            return false;
        };
        this.cancelCurveball = function(evt) {
            delete window.UA.curveballData;
            jQuery('#confirm-curveball-modal').modal('hide');
        };
        this.setCurveball = function(evt) {
            // serialize data from the curveball form AND
            // tack on data from the previous gateblock gate-button frm
            var $modal = jQuery('#confirm-curveball-modal');

            var $elt = $modal.find('.instructions');
            $elt.html('Setting the curveball. One moment...');
            $modal.find('.loading-spinner').removeClass('hidden');

            jQuery.ajax({
                type: 'POST',
                url: '.',
                data:  window.UA.curveballData,
                error: function() {
                    var msg = 'We\'re sorry! Something went wrong ' +
                        'setting the curveball. Please try again.';
                    alert(msg);
                    $modal.modal('hide');
                },
                success: function() {
                    $elt.html('Curveball is set.<br /><br />Please wait ' +
                              'while the facilitator panel is reloaded.');
                    window.location.reload();
                },
                done: function() {
                    delete window.UA.curveballData;
                }
            });
        };
        this.setFormClickHandler = function() {
            var btn = jQuery('.gate-block.active .gate-button form .btn');
            btn.css('cursor', 'pointer');
            btn.click(function() {
                var thisBtn = jQuery(this);
                window.lastPartOneBlock = thisBtn.closest(
                    '.gate-section-list').children('.part-1').last();
                window.btnBlock = thisBtn.closest('.part-1');
                window.lastBlockSec = window.lastPartOneBlock
                    .data('section-id');
                window.btnSec = window.btnBlock.data('section-id');
                thisBtn.unbind('click');
                thisBtn.css('cursor', 'not-allowed');
                var form  = jQuery(this).closest('form');
                var data = jQuery(form).serialize();
                var postUrl = window.location.pathname;
                jQuery.post(postUrl, data).error(function() {
                    var msg = 'I am sorry! There was a problem' +
                        ' opening the gate. Please refresh your' +
                        ' browser and try again.';
                    alert(msg);
                }).done(function() {
                    // Test to see if this is the last Part 1 gate.
                    // If so, reload the page to load in the part 2
                    // gate blocks.
                    if (typeof window.btnSec !== 'undefined') {
                        if (window.lastBlockSec === window.btnSec) {
                            window.location.reload();
                        }
                    }
                });
            });// end click
        };
        this.setPartsOnGateblocks = function() {
            var partOneElms = jQuery('.part1:first-child');
            var gsl = jQuery('.gate-section-list').length;
            var p2l = jQuery('.part2').length;

            partOneElms.each(function() {
                var html = '<div class="part1text">Part 1 </div>';
                jQuery(this).prepend(html);
            });
            if (p2l) {
                for (var i = 0; i < gsl ; i ++) {
                    var gs = jQuery('.gate-section-list').eq(i);
                    var part2 = gs.eq(0).find('.part2').eq(0);
                    if (part2.length > 0) {
                        var choice = part2.attr('class').split(' ').pop();
                        var divHtml = '<div class="part2text">Part 2 ';
                        choice = 'Choice ' + choice.split('-').pop();
                        divHtml += choice + ' </div>';
                        part2.prepend(divHtml);
                    }
                }
            }
        };
        this.setChoicesOnSecondParts = function() {
            var part2Gates = jQuery('.part2');
            var lastPart2Gates = [];
            part2Gates.parent().each(function() {
                var lastChild = jQuery(this).last();
                lastPart2Gates.push(lastChild);
            });
            for (var i = 0; i < lastPart2Gates.length; i ++) {
                var gate = lastPart2Gates[i];
                var choiceAttr = gate.children().last().attr(
                    'data-part-decision');
                var decision;
                if (choiceAttr.match('p2c2-')) {
                    var choice = choiceAttr.split('p2c2-')[1];
                    decision = 'Part 2 Second Decision ' + choice;
                } else {
                    decision = '';
                }
                gate.append(decision);
            }
        };
        this.impersonate = function() {
            jQuery('a.preview-link').click(function(e) {
                e.preventDefault();
                var destination = jQuery(this).attr('href');
                var userId = jQuery(this).data('user');
                var impersonateUrl = '/_impersonate/' + userId + '/';
                $.get(impersonateUrl).complete(function() {
                    window.open(destination, '_blank');
                });
            });
        };

        this.init();
    }
};

jQuery(document).ready(function() {
    window.UA = new UELCAdmin.Admin();

    var updateWidth = function() {
        var width = $('.gate-sections:first').outerWidth();
        $('.gate-sections .group-name:lt(4)').outerWidth(width);
    };

    $(window).resize(updateWidth);
    updateWidth();
});
