/* global admin: true */

jQuery(document).ready(function() {
    // create Admin class
    var UELCAdmin = function() {
        this.setMultiselects = function() {
            jQuery('.hierarchy-select').multiselect();
            jQuery('.case-select').multiselect();
            jQuery('.cohort-select').multiselect();
            jQuery('.user-select').multiselect();
            jQuery('.create-user-profile').multiselect();
        };

        this.addListeners = function() {
            jQuery('.form-submit').click(function() {
                var form = jQuery(this).parent();
                window.admin.submit(form);
            });

            jQuery('form').on('reset', function() {
                // eslint-disable-next-line scanjs-rules/call_setTimeout
                setTimeout(function() {
                    jQuery('.hierarchy-select')
                        .multiselect().multiselect('destroy')
                        .multiselect('refresh');
                    jQuery('.cohort-select')
                        .multiselect().multiselect('destroy')
                        .multiselect('refresh');
                    jQuery('.user-select')
                        .multiselect().multiselect('destroy')
                        .multiselect('refresh');
                    jQuery('.create-user-profile')
                        .multiselect().multiselect('destroy')
                        .multiselect('refresh');
                });
            });
        };

        this.formUpdate = function(form) {
            //console.log(form);
        };

        this.highlight = function(element) {
            jQuery(element).closest('.form-control')
                .parent().removeClass('success').addClass('has-error');
        };

        this.removeHighlight = function(element) {
            jQuery(element).addClass('valid')
                .parent().removeClass('has-error').addClass('success');
        };

        this.submit = function(form) {
            jQuery(form).validate({
                rules: {
                    name: {
                        minlength: 3,
                        required: true
                    },
                    url: {
                        required: true,
                    },
                    username: {
                        minlength: 3,
                        required: true,
                    },
                    password1: {
                        minlength: 3,
                        required: true,
                    },
                    password2: {
                        minlength: 3,
                        required: true,
                        equalTo: '#id_password1',
                    },
                    newPassword1: {
                        minlength: 3,
                        required: true,
                    },
                    newPassword2: {
                        minlength: 3,
                        required: true,
                        equalTo: '#id_newPassword1',
                    },
                    user: 'required',
                    hierarchy: 'required',
                    /*
                      cohort:{
                      required:true,
                      }
                    */
                },
                ignore: '.ignore',
                errorClass: 'has-error',
                // this is not is use at the moment
                /*
                  submitHandler: function(form) {
                  console.log(form);
                  action_url = jQuery(form).attr('action');
                  jQuery.post(action_url, jQuery(form).serialize(), function(data) {
                  console.log(data)
                  });
                  },
                */
                highlight: function(element) {
                    window.admin.highlight(element);
                },
                success: function(element) {
                    window.admin.removeHighlight(element);
                },
                error: function() {
                    alert('problem!');
                },
            });//end validate
        };

        this.resetForm = function(form) {
            jQuery(form).children('.reset-button').trigger('click');
            jQuery(form).find('input.form-control').each(function() {
                window.admin.removeHighlight(this);
            });
            jQuery(form).find('.control-label').each(function() {
                window.admin.removeHighlight(this);
            });
        };

        this.hierarchyCallback = function(data) {
            if (data.error) {
                jQuery('#add-hierarchy-form')
                    .find('input.form-control').each(function() {
                        window.admin.highlight(this);
                    });
                alert(data.error);
            }else {
                // success
                var elem = jQuery('.hierarchy-select');
                var html = '<option value=' + data.value + '>';
                html += data.name + '</option>';
                var form = jQuery('#add-hierarchy-form');
                elem.append(html);
                this.resetForm(form);
                var alertMsg = 'Your Hierarchy has been created! ' +
                    'It is available for editing,' +
                    'so go and add some content! ' +
                    'You can access it here: ' + data.url + 'edit/';
                alert(alertMsg);
            }
        };

        this.createUserCallback = function(data) {
            if (data.error) {
                jQuery('.create-user-profile')
                    .parent().parent().addClass('has-error');
                alert(data.error);
            }else {
                var elem = jQuery('.user-select');
                var html = '<option value=' + data.user + '>';
                html += data.username + '</option>';
                var form = jQuery('#add-user-form');
                elem.append(html);
                this.resetForm(form);
                alert('created user');
            }
        };

        this.editUserCallback = function(data) {
            if (data.error) {
                alert(data.error);
            }else {
                var userID = data.userID;
                var username = data.username;
                var profile = data.profile;
                var cohorts = data.cohorts;
                var row = jQuery('#user-' + userID);
                this.updateUserRow(row, username, profile, cohorts);
                var modal = jQuery('#edit-user-form-modal-' + userID);
                modal.modal('hide');
                alert('user has been updated successfully!');
            }
        };

        this.deleteUserCallback = function(data) {
            if (data.error) {
                alert(data.error);
            }else {
                var userID = data.userID;
                var modal = jQuery('#delete-user-form-modal-' + userID);
                var row = jQuery('#user-' + userID);
                modal.on('hidden.bs.modal', row, function() {
                    row.remove();
                });
                modal.modal('hide');
                alert('user has been deleted!');
            }
        };

        this.updateUserRow = function(row, username, profile, cohorts) {
            var tdUsername = jQuery(row).children('.td-username');
            var tdProfile = jQuery(row).children('.td-profile');
            var tdCohorts = jQuery(row).children('.td-cohorts');
            tdUsername.text(username);
            tdProfile.text(profile);
            tdCohorts.text(cohorts);
        };

        this.createCohortCallback = function(data) {
            if (data.error) {
                jQuery('#add-cohort-form')
                    .find('input.form-control').each(function() {
                        window.admin.highlight(this);
                    });
                alert(data.error);
            }else {
                // success
                var elem = jQuery('.cohort-select');
                var html = '<option value=' + data.cohort + '>';
                html += data.name + '</option>';
                elem.append(html);
                jQuery('.cohort-select')
                    .multiselect('destroy').multiselect('refresh');
                jQuery('#add-cohort-form').trigger('reset');
                jQuery('#add-cohort-form')
                    .find('input.form-control').each(function() {
                        window.admin.removeHighlight(this);
                    });
                alert('Cohort has been created!');
                jQuery('.user-select')
                    .multiselect('destroy').multiselect('refresh');
            }
        };

        this.createCaseCallback = function(data) {
            if (data.error) {
                jQuery('#add-case-form')
                    .find('input.form-control').each(function() {
                        window.admin.highlight(this);
                    });
                alert(data.error);
            }else {
                // success
                var form = jQuery('#add-case-form');
                this.resetForm(form);
                form.find('input.form-control').each(function() {
                    window.admin.removeHighlight(this);
                });
                alert('Case has been created!');
            }
        };

        this.checkForMessages = function() {
            if (jQuery('#message-modal').length > 0) {
                this.showMessageModal();
            }
        };

        this.showMessageModal = function() {
            var modal = jQuery('#message-modal');
            window.callback = modal.attr('data-callback');
            modal.modal('show');

        };

        this.setNavbarActiveTab = function() {
            var loc = window.location.href;
            var urlArray = loc.split('/');
            var page = urlArray[urlArray.length - 2];
            var activeLi = jQuery('li[data-tab="' + page + '"]');
            //console.log(activeLi);
            jQuery('#uelc-admin-menu ul li').each(function() {
                jQuery(this).removeClass('active');
            });
            activeLi.addClass('active');
        };

        this.init = function() {
            this.setMultiselects();
            this.addListeners();
            this.checkForMessages();
            this.setNavbarActiveTab();
        };
    };
    //Instantiate the class
    window.admin = new UELCAdmin();
    admin.init();

});
