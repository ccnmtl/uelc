var UELCAdmin; 
UELCAdmin = {
    Admin: function(){
        this.init = function(){
            //alert('init');
        };
        this.init();
    }
};

jQuery(document).ready(function(){
    var UA = new UELCAdmin.Admin();
});