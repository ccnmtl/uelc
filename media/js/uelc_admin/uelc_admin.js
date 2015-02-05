jQuery(document).ready(function(){
  // create Admin class
  var UELCAdmin = function(){
    this.setMultiselects = function(){
      jQuery('.hierarchy-select').multiselect();
      jQuery('.case-select').multiselect();
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

           // this is not is use at the moment
           /*
          submitHandler: function(form){

           
            
              console.log(form);
              action_url = jQuery(form).attr('action');
            
              jQuery.post(action_url, jQuery(form).serialize(), function(data){
                console.log(data)
              });
            
          },
          */

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
        profile = data.profile;
        cohorts = data.cohorts;
        row = jQuery('#user-'+user_id);
        this.updateUserRow(row, username, profile, cohorts);
        modal = jQuery('#edit-user-form-modal-'+user_id);
        modal.modal('hide');
        alert('user has been updated successfully!')
      }
    },

    this.deleteUserCallback = function(data){
      if(data.error){
        alert(data.error)
      }else{
        user_id = data.user_id
        modal = jQuery('#delete-user-form-modal-'+user_id);
        row = jQuery('#user-'+user_id);
        modal.on('hidden.bs.modal', row, function() {
           row.remove();
        })
        modal.modal('hide');
        alert('user has been deleted!')
      }
    },

    this.updateUserRow = function(row, username, profile, cohorts){

      td_username = jQuery(row).children('.td-username');
      td_profile = jQuery(row).children('.td-profile');
      td_cohorts = jQuery(row).children('.td-cohorts');
      td_username.text(username);
      td_profile.text(profile)
      td_cohorts.text(cohorts);
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
    this.checkForMessages = function(){
      if(jQuery('#message-modal').length > 0){
        this.showMessageModal();
      }
    },

    this.showMessageModal = function(){
      modal = jQuery('#message-modal')
      callback = modal.attr('data-callback');
      modal.modal('show');

    },

    this.init = function(){
      this.setMultiselects();
      this.addListeners();
      this.checkForMessages();
    }
  };

  //Instatntiate the class
  window.admin = new UELCAdmin();
  admin.init();

})