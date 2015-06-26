var UELCAdmin;
UELCAdmin = {
    Admin: function() {
        this.init = function() {
            this.setFormClickHandler();
            this.separateParts();

            this.setCurballBlockHandler();
            //this.setPartsOnGateblocks();
            //this.setChoicesOnSecondParts();
            //this.impersonate();
            /*
             jQuery('.library-item-user-select').multiselect();
             jQuery('[data-toggle="tooltip"]').tooltip({
                'placement': 'top'
            });
            this.deleteLibraryItem();
            */
        };
        this.setChoicesOnParts = function() {
            jQuery('.user-part2').each(function() {
                var partTwoHeader = jQuery('<div class="part2-header">Part 2</div>');
                var header = jQuery(this);
                var prevPartColumn = header.parent().children('.gate-section-list').eq(0);
                var responseText = prevPartColumn.find('.response').eq(1).text();
                jQuery(this).prepend(partTwoHeader);
                partTwoHeader.append(responseText);
            });
        };
        this.separateParts = function() {
            jQuery('.gate-section-list').each(function() {
                var partTwo = jQuery(this).children('.part-2');
                var wrapDiv = '<div class="gate-section-list well well-sm user-part2"></div>';
                var glyph = '<span class="glyphicon glyphicon-triangle-bottom" aria-hidden="true"></span>';
                partTwo.detach().wrapAll(wrapDiv).parent().insertAfter(this);
                jQuery(this).after(glyph);
            });
            this.setChoicesOnParts();

        };
        this.setCurballBlockHandler = function() {
            jQuery('.set-curveball').click(function() {
                var modal = jQuery(this).closest('.modal');
                var modId = modal.attr('id').split('-')[1];
                var form = jQuery('#curveball-form-' + modId);
                form.submit();
            });
        };
        this.separateParts = function() {
            jQuery('.gate-section-list').each(function() {
                var partTwo = jQuery(this).children('.part-2');
                var wrapDiv = '<div class="gate-section-list well well-sm">Part 2</div>';
                var glyph = '<span class="glyphicon glyphicon-triangle-bottom" aria-hidden="true"></span>';
                partTwo.detach().wrapAll(wrapDiv).parent().insertAfter(this);
                jQuery(this).after(glyph);
            })

        };
        this.setFormClickHandler = function() {
            var btn = jQuery('.gate-block.active .gate-button form .btn');
            btn.css('cursor', 'pointer');
            btn.click(function() {
                btn.unbind('click');
                btn.css('cursor', 'not-allowed');
                form  = jQuery(this).closest('form');
                data = jQuery(form).serialize();
                jQuery.post(
                    '/pages/case-one/facilitator/', data).error(function() {
                    var msg = 'I am sorry! There was a problem opening' +
                        ' the gate. Please refresh your browser and try again.';
                    alert(msg);
                });
            });
        };
        this.setPartsOnGateblocks = function() {
            var partOneElms = jQuery('.part1:first-child');
            var gsl = jQuery('.gate-section-list').length;
            var p2l = jQuery('.part2').length;

            partOneElms.each(function() {
                html = '<div class="part1text">Part 1 </div>';
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
                choiceAttr = gate.children().last().attr('data-part-decision');
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
                    //alert('fired');
                    window.open(destination, '_blank');
                });
            });
        };

        this.init();
    }
};

jQuery(document).ready(function() {
    window.UA = new UELCAdmin.Admin();
});
