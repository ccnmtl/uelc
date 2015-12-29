import json
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from pagetree.helpers import get_hierarchy
from pagetree.models import Hierarchy, Section
from pagetree.tests.factories import ModuleFactory
from uelc.main.models import Case
from uelc.main.tests.factories import (
    GroupUpFactory, AdminUpFactory,
    CaseFactory, CohortFactory, FacilitatorUpFactory,
    UELCModuleFactory, HierarchyFactory, CaseQuizFactory,
    QuestionFactory, AnswerFactory, CaseAnswerFactory
)


class BasicTest(TestCase):
    def setUp(self):
        self.c = self.client

    def test_root(self):
        response = self.c.get("/")
        self.assertEquals(response.status_code, 200)

    def test_smoketest(self):
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)


class PagetreeViewTestsLoggedOut(TestCase):
    def setUp(self):
        self.c = self.client
        self.h = get_hierarchy("main", "/pages/main/")
        self.root = self.h.get_root()
        self.root.add_child_section_from_dict(
            {
                'label': 'Section 1',
                'slug': 'section-1',
                'pageblocks': [],
                'children': [],
            })

    def test_page(self):
        r = self.c.get("/pages/main/section-1/")
        self.assertEqual(r.status_code, 302)

    def test_edit_page(self):
        r = self.c.get("/pages/main/edit/section-1/")
        self.assertEqual(r.status_code, 302)

    def test_instructor_page(self):
        r = self.c.get("/pages/main/instructor/section-1/")
        self.assertEqual(r.status_code, 302)


class PagetreeViewTestsLoggedIn(TestCase):
    def setUp(self):
        self.c = self.client
        self.h = get_hierarchy("main", "/pages/main/")
        self.root = self.h.get_root()
        self.root.add_child_section_from_dict(
            {
                'label': 'Section 1',
                'slug': 'section-1',
                'pageblocks': [],
                'children': [],
            })
        self.grp_usr_profile = GroupUpFactory()
        self.grp_usr_profile.user.set_password("test")
        self.grp_usr_profile.user.save()

        # Need a "Case" object associated with this hierarchy and this
        # user's cohort in order from them to be able to view it.
        case = CaseFactory(name='case-test', hierarchy=self.h)
        case.cohort.add(self.grp_usr_profile.cohort)

        self.c.login(
            username=self.grp_usr_profile.user.username,
            password="test")

    def test_page(self):
        r = self.c.get("/pages/main/section-1/")
        self.assertEqual(r.status_code, 302)

    def test_edit_page(self):
        r = self.c.get("/pages/main/edit/section-1/")
        self.assertEqual(r.status_code, 302)

    def test_instructor_page(self):
        r = self.c.get("/pages/main/instructor/section-1/")
        self.assertEqual(r.status_code, 200)


class TestGroupUserLoggedInViews(TestCase):
    def setUp(self):
        ModuleFactory("main", "/pages/main/")
        self.hierarchy = get_hierarchy(name='main')
        self.section = self.hierarchy.get_root().get_first_leaf()
        self.grp_usr_profile = GroupUpFactory()
        self.grp_usr_profile.user.set_password("test")
        self.grp_usr_profile.user.save()

        case = CaseFactory(name='case-test', hierarchy=self.hierarchy)
        case.cohort.add(self.grp_usr_profile.cohort)

        self.client.login(
            username=self.grp_usr_profile.user.username,
            password="test")

    def test_edit_page_form(self):
        response = self.client.get(self.section.get_edit_url())
        self.assertEqual(response.status_code, 302)

    def test_page(self):
        response = self.client.get(self.section.get_absolute_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 200)

    def test_index(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, 'main/index.html')


class TestFacilitatorLoggedInViews(TestCase):
    def setUp(self):
        ModuleFactory("main", "/pages/main/")
        self.hierarchy = get_hierarchy(name='main')
        self.section = self.hierarchy.get_root().get_first_leaf()
        self.facilitator_profile = FacilitatorUpFactory()
        self.facilitator_profile.user.set_password("test")
        self.facilitator_profile.user.save()

        case = CaseFactory(name='case-test', hierarchy=self.hierarchy)
        case.cohort.add(self.facilitator_profile.cohort)

        self.client.login(
            username=self.facilitator_profile.user.username,
            password="test")

    def test_edit_page_form(self):
        response = self.client.get(self.section.get_edit_url())
        self.assertEqual(response.status_code, 200)

    def test_page(self):
        response = self.client.get(self.section.get_absolute_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 200)

    def test_index(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, 'main/index.html')


class TestAdminBasicViews(TestCase):

    def setUp(self):
        self.h = get_hierarchy("main", "/pages/main/")
        self.root = self.h.get_root()
        self.root.add_child_section_from_dict(
            {
                'label': 'Section 1',
                'slug': 'section-1',
                'pageblocks': [],
                'children': [],
            })
        self.case = CaseFactory()
        self.profile = AdminUpFactory()
        self.gu = GroupUpFactory()
        self.cohort = CohortFactory()
        self.client.login(username=self.profile.user.username, password='test')

    def test_uelc_admin(self):
        request = self.client.get("/uelcadmin/", follow=True)
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed(request,
                                'pagetree/uelc_admin.html')

    def test_uelc_admin_case(self):
        request = self.client.get("/uelcadmin/case/", follow=True)
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed(request,
                                'pagetree/uelc_admin_case.html')

    def test_uelc_admin_create_hierarchy(self):
        request = self.client.post(
            "/uelcadmin/createhierarchy/", {'name': 'NewHierarchy'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_create_already_existing_hierarchy(self):
        response = self.client.post(
            "/uelcadmin/createhierarchy/", {'name': self.h.name},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/",
            follow=True)
        self.assertEqual(response.status_code, 200)
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        tmp_stg = "Hierarchy exists! Please use the exisiting one,\
                          or create one with a different name and url."
        er_msg = str(m[0])
        self.assertEqual(tmp_stg.strip(), er_msg.strip())

    def test_uelc_admin_create_cohort(self):
        request = self.client.post(
            "/uelcadmin/createcohort/", {'name': 'NewCohort'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_create_already_existing_cohort(self):
        request = self.client.post(
            "/uelcadmin/createcohort/", {'name': self.cohort.name},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_create_user(self):
        response = self.client.post(
            '/uelcadmin/createuser/',
            {
                'username': 'NewUser',
                'password1': 'magic_password',
                'password2': 'magic_password',
                'user_profile': 'assistant',
                'cohort': self.cohort.id,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER='/uelcadmin/')
        self.assertEqual(response.status_code, 302)
        u = User.objects.get(username='NewUser')
        self.assertEqual(u.username, 'NewUser', 'The user was not created.')
        self.assertTrue(u.profile.is_assistant(),
                        'The user is not an assistant.')

        # Test that I can log in as the created user with the
        # given password.
        self.client.get('/accounts/logout/')
        response = self.client.post(
            '/accounts/login/',
            {
                'username': 'NewUser',
                'password': 'magic_password',
            },
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Oops!')
        self.assertNotContains(response, 'Invalid username or password')

    def test_uelc_admin_create_already_existing_user(self):
        response = self.client.post(
            '/uelcadmin/createuser/',
            {
                'username': self.gu.user.username,
                'password1': 'magic_password',
                'password2': 'magic_password',
                'user_profile': 'assistant',
                'cohort': self.cohort.id,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER='/uelcadmin/',
            follow=True)
        self.assertEqual(response.status_code, 200)
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        tmp_stg = 'That username already exists! Please enter a new one.'
        er_msg = str(m[0])
        self.assertEqual(tmp_stg.strip(), er_msg.strip())

    def test_uelc_admin_create_user_missing_password1(self):
        request = self.client.post(
            "/uelcadmin/createuser/",
            {
                'username': 'NewUser',
                'password2': 'magic_password',
                'user_profile': 'assistant',
                'cohort': self.cohort.id
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER='/uelcadmin/')
        self.assertEqual(request.status_code, 302)
        self.assertEqual(
            User.objects.filter(username='NewUser').count(), 0,
            'The user was created.')

    def test_uelc_admin_create_user_missing_password2(self):
        request = self.client.post(
            "/uelcadmin/createuser/",
            {
                'username': 'NewUser',
                'password1': 'magic_password',
                'user_profile': 'assistant',
                'cohort': self.cohort.id
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER='/uelcadmin/')
        self.assertEqual(request.status_code, 302)
        self.assertEqual(
            User.objects.filter(username='NewUser').count(), 0,
            'The user was created.')

    def test_uelc_admin_create_user_mismatch_password(self):
        request = self.client.post(
            "/uelcadmin/createuser/",
            {
                'username': 'NewUser',
                'password1': 'magic_password',
                'password2': 'magic_password2',
                'user_profile': 'assistant',
                'cohort': self.cohort.id
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_REFERER='/uelcadmin/')
        self.assertEqual(request.status_code, 302)
        self.assertEqual(
            User.objects.filter(username='NewUser').count(), 0,
            'The user was created.')

    def test_uelc_admin_create_user_long_username(self):
        request = self.client.post(
            "/uelcadmin/createuser/",
            {
                'username': 'NewUserThatIsLongerThan30Characters',
                'password1': 'magic_password',
                'password2': 'magic_password',
                'user_profile': 'group_user',
                'cohort': self.cohort.id,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)
        self.assertFalse(
            User.objects.filter(
                username='NewUserThatIsLongerThan30Characters').exists())

    def test_uelc_admin_update_user(self):
        up = GroupUpFactory()
        request = self.client.post(
            "/uelcadmin/edituser/",
            {
                'user_id': up.user.pk,
                'username': 'some_random_name',
                'profile_type': up.profile_type,
                'cohort': up.cohort.pk,
            },
            follow=True)
        self.assertEqual(request.status_code, 200)
        self.assertTrue(
            User.objects.filter(username='some_random_name').exists())

    def test_uelc_admin_update_user_long_username(self):
        up = GroupUpFactory()
        original_username = up.user.username
        long_username = 'some_random_name_longer_than_30_characters'
        request = self.client.post(
            "/uelcadmin/edituser/",
            {
                'user_id': up.pk,
                'username': long_username,
                'profile_type': up.profile_type,
                'cohort': up.cohort.pk,
            },
            follow=True)
        self.assertEqual(request.status_code, 200)
        self.assertFalse(
            User.objects.filter(username=long_username).exists())
        self.assertTrue(
            User.objects.filter(username=original_username).exists())

    def test_uelc_admin_create_case(self):
        request = self.client.post(
            "/uelcadmin/createcase/",
            {'name': 'NewCase', 'hierarchy': str(self.h.id),
             'cohort': str(self.cohort.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_edit_cohort(self):
        request = self.client.post(
            "/uelcadmin/editcohort/",
            {'name': 'EditCohort', 'cohort_id': str(self.cohort.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_edit_user(self):
        request = self.client.post(
            "/uelcadmin/edituser/",
            {'username': 'EditUser', 'user_id': str(self.gu.user.pk),
             'profile_type': 'group_user', 'cohort': str(self.cohort.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_edit_non_existing_user(self):
        response = self.client.post(
            "/uelcadmin/edituser/",
            {'username': 'EditUser', 'user_id': '22',
             'profile_type': 'group_user', 'cohort': str(self.cohort.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/",
            follow=True)
        self.assertEqual(response.status_code, 200)
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        tmp_stg = 'User not found.'
        er_msg = str(m[0])
        self.assertEqual(tmp_stg.strip(), er_msg.strip())

    def test_uelc_admin_edit_case(self):
        request = self.client.post(
            "/uelcadmin/editcase/",
            {'name': 'EditCase', 'hierarchy': str(self.h.id),
             'cohort': str(self.cohort.id), 'case_id': str(self.case.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_delete_cohort(self):
        request = self.client.post(
            "/uelcadmin/deletecohort/", {'cohort_id': str(self.cohort.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_delete_user(self):
        request = self.client.post(
            "/uelcadmin/deleteuser/", {'user_id': str(self.gu.user.pk)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_delete_superuser(self):
        newsuperuser = AdminUpFactory()
        response = self.client.post(
            "/uelcadmin/deleteuser/", {'user_id': str(newsuperuser.user.pk)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/",
            follow=True)
        self.assertEqual(response.status_code, 200)
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        tmp_stg = "Sorry, you are not permitted to \
                      delete superuser accounts."
        er_msg = str(m[0])
        self.assertEqual(tmp_stg.strip(), er_msg.strip())

    def test_uelc_admin_delete_case(self):
        request = self.client.post(
            "/uelcadmin/deletecase/", {'case_id': str(self.case.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_delete_hierarchy(self):
        request = self.client.post(
            "/uelcadmin/deletehierarchy/", {'hierarchy_id': str(self.h.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_edit_user_password(self):
        response = self.client.get(
            '/uelcadmin/edituserpass/' + str(self.gu.user.pk) + '/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'pagetree/uelc_admin_user_pass_reset.html')
        self.assertIn('edit_user_pass_form', response.context)
        self.assertIn('user', response.context)

        response = self.client.post(
            '/uelcadmin/edituserpass/' + str(self.gu.user.pk) + '/',
            {
                'newPassword1': 'magic_password'
            },
            HTTP_REFERER='/uelcadmin/', follow=True)
        self.assertEqual(response.status_code, 200)
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        tmp_stg = "User password has been updated!"
        er_msg = str(m[0])
        self.assertEqual(tmp_stg.strip(), er_msg.strip())


class TestAdminErrorHandlingInCaseViews(TestCase):

    def setUp(self):
        self.h = get_hierarchy("main", "/pages/main/")
        self.root = self.h.get_root()
        self.root.add_child_section_from_dict(
            {
                'label': 'Section 1',
                'slug': 'section-1',
                'pageblocks': [],
                'children': [],
            })
        self.case = CaseFactory()
        self.profile = AdminUpFactory()
        self.gu = GroupUpFactory()
        self.cohort = CohortFactory()
        self.client.login(username=self.profile.user.username, password='test')

    def test_admin_create_case_no_duplicate_names(self):
        response = self.client.post(
            "/uelcadmin/createcase/",
            {'name': 'NewCase', 'hierarchy': str(self.h.id),
             'cohort': str(self.cohort.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/",
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/uelcadmin/')
        m = list(response.context['messages'])
        self.assertEqual(len(m), 0)

        '''Try to create a second Case with the same name.'''
        response2 = self.client.post(
            "/uelcadmin/createcase/",
            {'name': 'NewCase', 'hierarchy': str(self.h.id),
             'cohort': str(self.cohort.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/",
            follow=True)
        self.assertEqual(response2.status_code, 200)
        self.assertRedirects(response2, '/uelcadmin/')
        m = list(response2.context['messages'])
        self.assertEqual(len(m), 1)
        self.assertEqual(len(list(response2.context['messages'])), 1)
        tmp_stg = 'Case with this name already exists!' + \
            '                      Please use existing case or rename.'
        er_msg = str(m[0]).strip()
        self.assertEqual(tmp_stg.strip(), er_msg)

    def test_admin_create_case_no_case_for_hierarchy(self):
        '''Submit request to associate case with hierarchy'''
        response = self.client.post(
            "/uelcadmin/createcase/",
            {'name': 'NewCase1', 'hierarchy': str(self.h.id),
             'cohort': str(self.cohort.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/",
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/uelcadmin/')
        m = list(response.context['messages'])
        self.assertEqual(len(m), 0)

        '''Attempt to create second case for the hierarchy'''
        response2 = self.client.post(
            "/uelcadmin/createcase/",
            {'name': 'NewCase2', 'hierarchy': str(self.h.id),
             'cohort': str(self.cohort.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/",
            follow=True)
        self.assertEqual(response2.status_code, 200)
        self.assertRedirects(response2, '/uelcadmin/')
        m = list(response2.context['messages'])
        self.assertEqual(len(m), 1)
        tmp_stg = (
            'Case already exists! A case has already' +
            '                      been created that is attached to the' +
            '                      selected hierarchy. Do you need to create' +
            '                      another hierarchy or should you use' +
            '                      an existing case?')
        er_msg = str(m[0])
        self.assertEqual(tmp_stg.strip(), er_msg.strip())

    def test_admin_edit_case_case_for_hierarchy_exists(self):
        '''Submit request to associate case with hierarchy'''
        ModuleFactory("newmain", "/pages/newmain/")
        self.newhierarchy = get_hierarchy(name='newmain')
        self.hierarchy_case = CaseFactory(name="HierarchyCase",
                                          hierarchy=self.newhierarchy)
        '''Attempt to create second case for the hierarchy'''
        response = self.client.post(
            "/uelcadmin/createcase/",
            {'name': self.hierarchy_case.name,
             'hierarchy': str(self.newhierarchy.id),
             'cohort': str(self.cohort.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/",
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/uelcadmin/')
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        tmp_stg = 'Case with this name already exists!' + \
            '                      Please use existing case or rename.'
        er_msg = str(m[0])
        self.assertEqual(tmp_stg.strip(), er_msg.strip())

    def test_admin_edit_case_no_emptyfields(self):
        '''This functionality doesn't actually work...'''
        pass

    def test_admin_create_case_no_emptyfields(self):
        '''This functionality doesn't actually work...'''
        pass


class TestAdminCohortViewContext(TestCase):

    def setUp(self):
        self.h = get_hierarchy("main", "/pages/main/")
        self.root = self.h.get_root()
        self.root.add_child_section_from_dict(
            {
                'label': 'Section 1',
                'slug': 'section-1',
                'pageblocks': [],
                'children': [],
            })
        self.case = CaseFactory()
        self.profile = AdminUpFactory()
        self.gu = GroupUpFactory()
        self.cohort = CohortFactory()
        self.client.login(username=self.profile.user.username, password='test')

    def test_uelc_admin_case_response_context(self):
        response = self.client.get("/uelcadmin/cohort/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'pagetree/uelc_admin_cohort.html')
        self.assertIn('path', response.context)
        self.assertIn('casemodel', response.context)
        self.assertIn('cohortmodel', response.context)
        self.assertIn('create_user_form', response.context)
        self.assertIn('create_hierarchy_form', response.context)
        self.assertIn('users', response.context)
        self.assertIn('hierarchies', response.context)
        self.assertIn('cases', response.context)
        self.assertIn('cohorts', response.context)


class TestAdminUserViewContext(TestCase):

    def setUp(self):
        self.h = get_hierarchy("main", "/pages/main/")
        self.root = self.h.get_root()
        self.root.add_child_section_from_dict(
            {
                'label': 'Section 1',
                'slug': 'section-1',
                'pageblocks': [],
                'children': [],
            })
        self.case = CaseFactory()
        self.profile = AdminUpFactory()
        self.gu = GroupUpFactory()
        self.cohort = CohortFactory()
        self.client.login(username=self.profile.user.username, password='test')

    def test_uelc_admin_case_response_context(self):
        response = self.client.get("/uelcadmin/user/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'pagetree/uelc_admin_user.html')
        self.assertIn('path', response.context)
        self.assertIn('casemodel', response.context)
        self.assertIn('cohortmodel', response.context)
        self.assertIn('create_user_form', response.context)
        self.assertIn('create_hierarchy_form', response.context)
        self.assertIn('users', response.context)
        self.assertIn('hierarchies', response.context)
        self.assertIn('cases', response.context)
        self.assertIn('cohorts', response.context)


class TestFacilitatorTokenView(TestCase):
    def setUp(self):
        HierarchyFactory(name='main', base_url='/pages/main/')
        self.usr_profile = FacilitatorUpFactory()
        self.usr_profile.user.set_password("test")
        self.usr_profile.user.save()
        self.client.login(
            username=self.usr_profile.user.username,
            password="test")

    def test_get(self):
        response = self.client.get("/facilitator/fresh_token/")
        self.assertEqual(response.status_code, 200)

        token = json.loads(response.content)
        self.assertNotEqual(token, {})


class TestFreshGrpTokenView(TestCase):
    def setUp(self):
        UELCModuleFactory()
        self.grp_usr_profile = GroupUpFactory()
        self.grp_usr_profile.user.set_password("test")
        self.grp_usr_profile.user.save()
        self.client.login(
            username=self.grp_usr_profile.user.username,
            password="test")

    def test_get(self):
        s = Section.objects.first()
        response = self.client.get("/group_user/fresh_token/{}/".format(s.pk))
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content)
        self.assertNotEqual(token, {})


class TestCaseQuizViews(TestCase):

    def setUp(self):
        self.h = get_hierarchy("main", "/pages/main/")
        self.root = self.h.get_root()
        self.root.add_child_section_from_dict(
            {
                'label': 'Section 1',
                'slug': 'section-1',
                'pageblocks': [],
                'children': [],
            })
        self.case = CaseFactory()
        self.case_quiz = CaseQuizFactory()
        self.profile = AdminUpFactory()
        self.gu = GroupUpFactory()
        self.cohort = CohortFactory()
        self.client.login(username=self.profile.user.username, password='test')

    def test_admin_add_case_answer_get(self):
        '''First test the 404 response for non-existant question'''
        request = self.client.get("/edit_question/0/add_case_answer/")
        self.assertEqual(request.status_code, 404)
        self.assertTemplateUsed(request,
                                '404.html')
        '''Add question to quiz and check that it is rendered with
        the correct template'''
        question = QuestionFactory(quiz=self.case_quiz)
        request = self.client.get(
            "/edit_question/" + str(question.pk) + "/add_case_answer/")
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed(request,
                                'quizblock/edit_question.html')

    def test_admin_add_case_answer_post_valid_values(self):
        question = QuestionFactory(quiz=self.case_quiz)
        '''Submit a request'''
        request = self.client.post(
            "/edit_question/" + str(question.pk) + "/add_case_answer/",
            {'value': 5, 'title': 'title'})
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed(request,
                                'quizblock/edit_question.html')

    def test_admin_add_case_answer_post_missing_title(self):
        question = QuestionFactory(quiz=self.case_quiz)
        response = self.client.post(
            "/edit_question/" + str(question.pk) + "/add_case_answer/",
            {'value': 5, 'title': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'quizblock/edit_question.html')
        self.assertIn('question', response.context)
        self.assertIn('case_answer_form', response.context)

    def test_admin_edit_case_answer_get(self):
        ca = CaseAnswerFactory(
            answer=AnswerFactory(
                question=QuestionFactory(quiz=self.case_quiz)))
        response = self.client.get(
            "/edit_case_answer/" + str(ca.pk) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'quizblock/edit_answer.html')
        self.assertIn('case_answer', response.context)
        self.assertIn('case_answer_form', response.context)

    def test_admin_edit_case_answer_post(self):
        ca = CaseAnswerFactory(
            answer=AnswerFactory(
                question=QuestionFactory(quiz=self.case_quiz)))
        response = self.client.post(
            "/edit_case_answer/" + str(ca.pk) + "/",
            {'value': ca.answer.value, 'title': ca.title,
             'description': ca.description})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'quizblock/edit_answer.html')
        self.assertIn('case_answer', response.context)
        self.assertIn('case_answer_form', response.context)

    def test_admin_delete_case_answer_post(self):
        ca = CaseAnswerFactory(
            answer=AnswerFactory(
                question=QuestionFactory(quiz=self.case_quiz)))
        response = self.client.post(
            "/edit_question/" + str(ca.pk) + "/delete_case_answer/",
            {})
        self.assertEqual(response.status_code, 302)


class ClonedModuleFactoryTest(TestCase):
    def setUp(self):
        UELCModuleFactory()
        h = Hierarchy.objects.get(name='case-test')

        self.profile = AdminUpFactory()
        self.client.login(username=self.profile.user.username, password='test')

        self.cloned_hier = Hierarchy.clone(h, 'cloned', '/pages/cloned/')
        case = CaseFactory(name='case-cloned', hierarchy=self.cloned_hier)
        case.cohort.add(self.profile.cohort)

    def test_can_view_part_one(self):
        r = self.client.get('/pages/cloned/part-1/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Edit Page')
        self.assertContains(r, 'These elements use Bootstrap for styling.')

    def test_can_view_intro_page(self):
        r = self.client.get('/pages/cloned/part-1/intro/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Edit Page')

    def test_can_view_decision_block(self):
        r = self.client.get('/pages/cloned/part-1/your-first-decision/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Edit Page')
        self.assertContains(r, 'Select One')

    def test_can_view_curveball(self):
        r = self.client.get(
            '/pages/cloned/part-1/your-first-decision/curve-ball/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Edit Page')

    def test_can_view_curveball_confirmation(self):
        r = self.client.get(
            '/pages/cloned/part-1/your-first-decision/curve-ball/'
            'confirm-first-decision/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Edit Page')
        self.assertContains(r, 'Confirm First Decision')


class CloneHierarchyWithCasesViewTest(TestCase):
    def setUp(self):
        UELCModuleFactory()
        self.h = Hierarchy.objects.get(name='case-test')
        self.profile = AdminUpFactory()
        self.client.login(username=self.profile.user.username, password='test')
        self.case = Case.objects.get(name='case-test')
        self.case.cohort.add(self.profile.cohort)

    def test_get(self):
        url = reverse('clone-hierarchy', kwargs={
            'hierarchy_id': self.h.pk
        })
        r = self.client.get(url)

        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Clone {}'.format(self.h.name))

    def test_post(self):
        url = reverse('clone-hierarchy', kwargs={
            'hierarchy_id': self.h.pk
        })
        r = self.client.post(url, {
            'name': 'test',
            'base_url': '/pages/test/',
        })

        self.assertEqual(r.status_code, 302)
        self.assertEqual(Hierarchy.objects.filter(name='test').count(), 1)

        cloned_h = Hierarchy.objects.get(name='test')
        self.assertEqual(Case.objects.filter(hierarchy=cloned_h).count(), 1)

        cloned_case = Case.objects.filter(hierarchy=cloned_h).first()
        self.assertEqual(cloned_case.name, self.case.name)
        self.assertEqual(cloned_case.description, self.case.description)
        self.assertEqual(cloned_case.cohort.count(), self.case.cohort.count())
        self.assertEqual(set(cloned_case.cohort.all()),
                         set(self.case.cohort.all()))
