var UELCAdmin;
UELCAdmin = {
    Admin: function() {
        this.init = function() {
            this.setFormClickHandler();
            this.separateParts();
            this.setCurveballBlockHandler();
            this.setCurveballCommitAccess();
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
                thisBtn = jQuery(this);
                decisionBadge = thisBtn.closest(
                    '.gate-block').prev().find('.badge');
                decisionStatus = decisionBadge.text();
                if (decisionStatus !== "reviewed") {
                    thisBtn.css('cursor', 'not-allowed');
                    thisBtn.attr('data-toggle', '');
                    thisBtn.click(function() {
                        var msg = 'You must wait until the' +
                        ' group has confirmed their decision!' +
                        ' Please remind the group user to' +
                        ' select a choice and confirm their' +
                        ' choice.';
                        alert(msg);
                    });
                }else {
                    thisBtn.unbind('click');
                    thisBtn.css('cursor', 'pointer');
                    thisBtn.attr('data-toggle', 'modal');
                }
            });
        };
        this.setCurveballBlockHandler = function() {
            jQuery('.set-curveball').click(function() {
                var lgf = jQuery(this).parent().parent().find(
                    '.loading-spinner');
                var modal = jQuery(this).closest('.modal');
                var modId = modal.attr('id').split('CurveballModal-')[1];
                var cbForm = jQuery('#curveball-form-' + modId);
                var cbFormData = cbForm.serialize();
                var postUrl = window.location.pathname;
                var gate = jQuery(cbForm).parent().parent();
                var prevForm = gate.parent().prev().find('.gate-button form');
                var prevFormData = prevForm.serialize();
                window.UA.tempForm = prevForm;
                lgf.removeClass('hidden');
                jQuery.post(postUrl, cbFormData).fail(function() {
                    var msg = 'We are sorry! Something went wrong with ' +
                    'setting the curveball. Please Try again.';
                    alert(msg);
                }).success(function() {
                    var formData = window.UA.tempForm.serialize();
                    var postUrl = window.location.pathname;
                    jQuery.post(postUrl, formData).fail(function() {
                        var msg = 'We are sorry! Something went wrong ' +
                        'with opening the gate. Please refresh your ' +
                        'browser and continue.';
                    });
                }).done(function() {
                    window.location.reload();
                });
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
                window.lastBlockSec = lastPartOneBlock.data('section-id');
                window.btnSec = btnBlock.data('section-id');
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
                lastChild = jQuery(this).last();
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
