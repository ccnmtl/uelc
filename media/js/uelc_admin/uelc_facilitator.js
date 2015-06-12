var UELCAdmin;
UELCAdmin = {
    Admin: function() {
        this.init = function() {
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
        /*
        this.deleteLibraryItem = function() {
            jQuery('.library-item-admin .glyphicon-trash').click(function() {
                var retVal = confirm('Do you want to delete the item?');
                if (retVal === true) {
                    tr = jQuery(this).parent().parent();
                    td = tr.children('.library-item-document')
                           .children('span').text();
                    data = {
                            'library-item-delete':true,
                            'library_item_id': td
                            };
                    window.url = window.location.href;
                    jQuery.post(url, data).done(function() {
                        alert('Item deleted');
                        window.location = window.url;
                    });
                }
            });
        };
        */

        this.init();
    }
};

jQuery(document).ready(function() {
    window.UA = new UELCAdmin.Admin();
});
