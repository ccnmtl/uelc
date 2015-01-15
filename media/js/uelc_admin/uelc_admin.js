var UELCAdmin; 
UELCAdmin = {
    Admin: function(){
        this.init = function(){
        	jQuery('#library-item-user-select').multiselect();
            jQuery('[data-toggle="tooltip"]').tooltip({
			    'placement': 'top'
			});
			this.remove_left_nav_column()
        },
        this.remove_left_nav_column = function(){
        	jQuery('.col-md-2').remove();
        }
        this.init();
    }
};




jQuery(document).ready(function(){
	window.UA = new UELCAdmin.Admin();    
});