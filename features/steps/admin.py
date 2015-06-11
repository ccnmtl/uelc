import time
from behave import then, when
from django.contrib.auth.models import User


@when(u'I fill out the create user form for user "{username}"')
def i_fill_out_the_create_user_form_for_user(context, username):
    b = context.browser
    b.fill('username', username)
    b.fill('password1', 'testpass')
    b.fill('password2', 'testpass')
    b.find_by_css('#users button.multiselect')[1].click()
    b.find_by_css(
        '#users ul.multiselect-container'
    )[1].find_by_css('label')[1].click()


@when(u'I click the user modal submit button')
def i_click_the_user_modal_submit_button(context):
    time.sleep(1)
    context.browser.find_by_css('#users input[type="submit"]').first.click()


@then(u'the user "{username}" exists')
def the_user_exists(context, username):
    assert User.objects.filter(username=username).exists()
