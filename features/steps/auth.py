import urlparse
from behave import given, when
from uelc.main.models import Case, UserProfile
from uelc.main.tests.factories import AdminUpFactory, GroupUpFactory


def sign_in_as(context, usertype='group user'):
    if usertype == 'admin':
        up = AdminUpFactory()
        user = up.user
    else:
        up = GroupUpFactory()
        user = up.user

    # Add the user's cohort to the case
    case = Case.objects.first()
    case.cohort.add(up.cohort)

    b = context.browser
    b.visit(urlparse.urljoin(context.base_url, '/'))
    b.fill('username', user.username)
    b.fill('password', 'test')
    b.find_by_css('#login-local [type="submit"]').first.click()


@when(u'I sign out')
def i_sign_out(context):
    context.browser.find_link_by_partial_href('/accounts/logout/').click()


@when(u'I sign in as a "{usertype}"')
def i_sign_in_as_a(context, usertype):
    sign_in_as(context, usertype)


@when(u'I attach the admins to the group user\'s cohort')
def attach_the_admins_to_the_group_users_cohort(context):
    cohort = UserProfile.objects.filter(
        profile_type='group_user').first().cohort
    for admin in UserProfile.objects.filter(profile_type='admin'):
        admin.cohort = cohort
        admin.save()


@given(u'I am signed in as a "{usertype}"')
def i_am_signed_in_as_a(context, usertype):
    sign_in_as(context, usertype)
