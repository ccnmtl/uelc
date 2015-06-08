import urlparse
from behave import given
from uelc.main.tests.factories import AdminUserFactory, GroupUserFactory


def sign_in_as(context, usertype='group user'):
    if usertype == 'admin':
        user = AdminUserFactory()
    else:
        user = GroupUserFactory()

    password = 'test_pass1'
    user.set_password(password)
    user.save()

    b = context.browser
    b.visit(urlparse.urljoin(context.base_url, '/'))
    b.fill('username', user.username)
    b.fill('password', password)
    b.find_by_css('#login-local [type="submit"]').first.click()


@given(u'I am signed in as a "{usertype}"')
def i_am_signed_in_as_a(context, usertype):
    sign_in_as(context, usertype)
