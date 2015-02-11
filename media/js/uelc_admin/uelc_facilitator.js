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
            var gsl = jQuery('.gate-section-list').length;
            var p2l = jQuery('.part2').length;

            partOneElms.each(function() {
                html = "<div class='part1text'>Part 1 </div>";
                jQuery(this).prepend(html)
            })
            
            if (p2l){
                for(var i=0;i<gsl;i++){
                    var gs = jQuery('.gate-section-list').eq(i);
                    var part2 = gs.eq(0).find('.part2').eq(0);
                    var choice = part2.attr('class').split(' ').pop()
                    part2.prepend('<div class="part2text">Part 2 ' + choice + ' </div>');

                };
            }
        
        };
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
