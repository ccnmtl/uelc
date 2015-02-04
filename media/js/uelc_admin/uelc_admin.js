jQuery(document).ready(function(){
  // create Admin class
  var UELCAdmin = function(){
    this.setMultiselects = function(){
      jQuery('.hierarchy-select').multiselect();
      jQuery('.cohort-select').multiselect();
      jQuery('.user-select').multiselect();
      jQuery('.create-user-profile').multiselect();

    },

    this.addListeners = function(){
      jQuery('.form-submit').click(function(){
        var form = jQuery(this).parent()
        window.admin.submit(form);
      })
      jQuery('form').on('reset', function(){
        setTimeout(function(){
          jQuery('.hierarchy-select').multiselect().multiselect('destroy').multiselect('refresh');;
          jQuery('.cohort-select').multiselect().multiselect('destroy').multiselect('refresh');;
          jQuery('.user-select').multiselect().multiselect('destroy').multiselect('refresh');;
          jQuery('.create-user-profile').multiselect().multiselect('destroy').multiselect('refresh');;
        })
      })
    },

    this.formUpdate = function(form){
      console.log(form);
    },

    this.highlight = function(element){
      jQuery(element).closest('.form-control').parent().removeClass('success').addClass('has-error');
    },

    this.removeHighlight = function(element){
      jQuery(element).addClass('valid').parent().removeClass('has-error').addClass('success');
    }

    this.submit = function(form){
      jQuery(form).validate({

          rules: {
              name: {
                  minlength: 3,
                  required: true
              },
              url: {
                  required: true,
              },
              username:{
                minlength: 3,
                required: true,
              },
              password1:{
                minlength: 3,
                required: true,
              },
              password2:{
                minlength: 3,
                required: true,
                equalTo : "#id_password1",
              },
              user: "required",

              hierarchy: "required",
              
              cohort:{
                required:true,
              }
          },          
          
          ignore: '.ignore',
          
          errorClass: 'has-error',

          submitHandler: function(form){
            jQuery.post( "/uelcadmin/", jQuery(form).serialize(), function(data){
              window.admin[data.action](data.action_args);
            });
          },

          highlight: function (element) {
              window.admin.highlight(element);
          },
          success: function (element) {
              window.admin.removeHighlight(element);
          },
          error: function(){
            alert('problem!');
          },
        });//end validate
    },

    this.resetForm = function(form){
      jQuery(form).children('.reset-button').trigger('click');
      jQuery(form).find('input.form-control').each(function(){
          window.admin.removeHighlight(this);
      });
      jQuery(form).find('.control-label').each(function(){
        window.admin.removeHighlight(this);
      })
    },

    this.hierarchyCallback = function(data){
      if(data.error){
        jQuery('#add-hierarchy-form').find('input.form-control').each(function(){
          window.admin.highlight(this);  
        })
        alert(data.error);
      }else{
        // success
        elem = jQuery('.hierarchy-select');
        html = '<option value='+data.value+'>'+data.name+'</option>';
        form = jQuery('#add-hierarchy-form');
        elem.append(html);
        this.resetForm(form);
        alert('Your Hierarchy has been created! It is available for editing,\
          so go and add some content! You can access it here,'+data.url+'edit/');
      }
    },

    this.createUserCallback = function(data){
      if(data.error){
        jQuery('.create-user-profile').parent().parent().addClass('has-error')
        alert(data.error);
      }else{
        elem = jQuery('.user-select');
        html = '<option value='+data.user+'>'+data.username+'</option>';
        form = jQuery('#add-user-form');
        elem.append(html);
        this.resetForm(form);
        alert('created user');
      }
    },
    this.editUserCallback = function(data){
      if(data.error){
        alert(data.error)
      }else{
        user_id = data.user_id;
        username = data.username;
        row = jQuery('#user-'+user_id);
        this.updateUserRow(row, username);
        modal = jQuery('#edit-user-form-modal-'+user_id);
        modal.modal('hide')
        alert('user has been updated successfully!')
      }
    },

    this.updateUserRow = function(row, username){
      console.log(row);
      console.log(username);
      td_username = jQuery(row).children('.td-username');
      td_username.text(username);
    },

    this.createCohortCallback = function(data){
      if(data.error){
        jQuery('#add-cohort-form').find('input.form-control').each(function(){
          window.admin.highlight(this);  
        })
        alert(data.error);

      }else{
        // success
        elem = jQuery('.cohort-select');
        html = '<option value='+data.cohort+'>'+data.name+'</option>';
        elem.append(html)
        jQuery('.cohort-select').multiselect('destroy').multiselect('refresh');
        jQuery('#add-cohort-form').trigger("reset");
        jQuery('#add-cohort-form').find('input.form-control').each(function(){
          window.admin.removeHighlight(this);  
        })
        alert('Cohort has been created!');
        jQuery('.user-select').multiselect('destroy').multiselect('refresh');
      }
    },

    this.createCaseCallback = function(data){
      if(data.error){
        jQuery('#add-case-form').find('input.form-control').each(function(){
          window.admin.highlight(this);  
        })
        alert(data.error);
        
      }else{
        // success
        form = jQuery('#add-case-form');
        this.resetForm(form);
        form.find('input.form-control').each(function(){
          window.admin.removeHighlight(this);  
        })
        alert('Case has been created!');
      }
    },

    this.init = function(){
      this.setMultiselects();
      this.addListeners();
    }
  };

  //Instatntiate the class
  window.admin = new UELCAdmin();
  admin.init();

})