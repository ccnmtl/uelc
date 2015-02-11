var UELCAdmin;
UELCAdmin = {
    Admin: function() {
        this.init = function() {
            this.set_parts_on_gateblocks();
            jQuery('.library-item-user-select').multiselect();
            jQuery('[data-toggle="tooltip"]').tooltip({
                'placement': 'top'
            });
            this.deleteLibraryItem();
        };
        this.set_parts_on_gateblocks = function() {
            var partOneElms = jQuery('.part1:first-child');
            var partTwoElms = [];
            partTwoElms.push(jQuery('.part1:last').next())
            partTwoElms.push(jQuery('.part1:first').parent()
                .find('.part1').last().next())
            partOneElms.each(function() {
                html = "<div class='part1text'>Part 1 </div>";
                jQuery(this).prepend(html)
            })

            for (i = 0; i < partTwoElms.length; i++) {
                    var elm = partTwoElms[i];
                    var classname = elm.attr('class')
                    var html2;
                    console.log(elm.hasClass('part2choice2'));
                    switch(elm) {
                        case elm.hasClass("part2choice1"):
                            html2 = jQuery("<div class='part2text'>Part 2 choice 1</div>");
                            break;
                        case elm.hasClass("part2choice2"):
                            html2 = jQuery("<div class='part2text'>Part 2 choice 2</div>");
                            break;
                        case elm.hasClass("part2choice3"):
                            html2 = jQuery("<div class='part2text'>Part 2 choice 3</div>");
                            break;
                    }
                    elm.prepend(html2)
            }
        
        }
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

        this.init();
    }
};

jQuery(document).ready(function() {
    window.UA = new UELCAdmin.Admin();
});
