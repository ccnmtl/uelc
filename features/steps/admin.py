import time
from behave import then, when
from django.contrib.auth.models import User
from pagetree.models import Hierarchy
from uelc.main.models import Case


@when(u'I fill out the create case form for "{casename}"')
def i_fill_out_the_create_case_form_for(context, casename):
    time.sleep(1)
    b = context.browser
    b.fill('name', casename)
    b.find_by_css('#cases [name="description"]').fill('Testing description')
    for i in range(2):
        el = b.find_by_css('#cases button.multiselect')[i]
        el.click()
        el.find_by_xpath('..//label')[-1].click()


@when(u'I fill out the create hierarchy form for "{hierarchyname}"')
def i_fill_out_the_create_hierarchy_form_for(context, hierarchyname):
    time.sleep(1)
    b = context.browser
    b.find_by_css(
        '#add-hierarchy-form-modal input[name="name"]').fill(hierarchyname)


@when(u'I fill out the create user form for "{username}"')
def i_fill_out_the_create_user_form_for(context, username):
    b = context.browser
    b.fill('username', username)
    b.fill('password1', 'testpass')
    b.fill('password2', 'testpass')
    el = b.find_by_css('#users button.multiselect')[1]
    el.click()
    el.find_by_xpath('..//label')[-1].click()


@when(u'I click the modal submit button for "{modaltype}"')
def i_click_the_modal_submit_button(context, modaltype):
    time.sleep(1)
    context.browser.find_by_css(
        '{} input[type="submit"]'.format(modaltype)).first.click()


@then(u'the case "{casename}" exists')
def the_case_exists(context, casename):
    assert Case.objects.filter(name=casename).exists()


@then(u'the hierarchy "{hierarchyname}" doesn\'t exist')
def the_hierarchy_doesnt_exist(context, hierarchyname):
    assert Hierarchy.objects.filter(name=hierarchyname).count() == 0


@then(u'the hierarchy "{hierarchyname}" exists')
def the_hierarchy_exists(context, hierarchyname):
    assert Hierarchy.objects.filter(name=hierarchyname).exists()


@then(u'the user "{username}" exists')
def the_user_exists(context, username):
    assert User.objects.filter(username=username).exists()
