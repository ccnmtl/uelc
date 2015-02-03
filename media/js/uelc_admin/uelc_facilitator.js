var UELCAdmin;
UELCAdmin = {
    Admin: function() {
        this.init = function() {
            jQuery('.library-item-user-select').multiselect();
            jQuery('[data-toggle="tooltip"]').tooltip({
                'placement': 'top'
            });

            this.deleteLibraryItem();
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
