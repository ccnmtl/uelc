from behave import given
from uelc.main.tests.factories import GroupUserFactory


@given(u'I am signed in as a group user')
def i_am_signed_in_as_a_group_user(context):
    user = GroupUserFactory()
    password = 'test_pass1'
    user.set_password(password)
    user.save()

    b = context.browser
    b.fill('username', user.username)
    b.fill('password', password)
    b.find_by_css('#login-local [type="submit"]').first.click()
