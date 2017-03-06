import json

from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from pagetree.helpers import get_hierarchy
from pagetree.models import Hierarchy, Section, UserPageVisit, UserLocation
from pagetree.tests.factories import ModuleFactory, UserPageVisitFactory
from quizblock.models import Question, Answer

from curveball.models import CurveballSubmission, CurveballBlock
from curveball.tests.factories import CurveballFactory,\
    CurveballSubmissionFactory
from gate_block.models import GateSubmission, SectionSubmission, GateBlock
from gate_block.tests.factories import SectionSubmissionFactory,\
    GateSubmissionFactory
from uelc.main.helper_functions import content_blocks_by_hierarchy_and_class
from uelc.main.models import Case, CaseMap, CaseQuiz, CaseAnswer
from uelc.main.tests.factories import (
    GroupUpFactory, AdminUpFactory,
    CaseFactory, CaseMapFactory, CohortFactory, FacilitatorUpFactory,
    UELCModuleFactory, HierarchyFactory, CaseQuizFactory,
    QuestionFactory, AnswerFactory, CaseAnswerFactory
)
from uelc.main.views import UELCPageView, FacilitatorView


class BasicTest(TestCase):
    def setUp(self):
        self.c = self.client

    def test_root(self):
        response = self.c.get("/")
        self.assertEquals(response.status_code, 200)

    def test_smoketest(self):
        self.c.get("/smoketest/")


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

    def test_uelc_admin_create_case(self):
        request = self.client.post(
            "/uelcadmin/createcase/",
            {'name': 'NewCase', 'hierarchy': str(self.h.id),
             'cohort': str(self.cohort.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_edit_cohort(self):
        url = reverse('uelcadmin-edit-cohort', kwargs={'pk': self.cohort.id})
        request = self.client.post(
            url, {'name': 'EditCohort'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_edit_user(self):
        url = reverse('uelcadmin-edit-user', kwargs={'pk': self.gu.user.id})
        data = {
            'username': 'EditUser',
            'profile_type': 'group_user',
            'cohort': str(self.cohort.id)
        }
        request = self.client.post(
            url, data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_edit_user_no_profile(self):
        u_no_profile = User.objects.create(username='no_profile')
        url = reverse('uelcadmin-edit-user', kwargs={'pk': u_no_profile.id})

        data = {
            'username': 'EditUser',
            'profile_type': 'group_user',
            'cohort': str(self.cohort.id)
        }

        request = self.client.post(
            url, data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

    def test_uelc_admin_edit_non_existing_user(self):
        url = reverse('uelcadmin-edit-user', kwargs={'pk': 22})
        data = {
            'username': 'EditUser',
            'profile_type': 'group_user',
            'cohort': str(self.cohort.id)
        }

        response = self.client.post(
            url, data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/",
            follow=True)
        self.assertEqual(response.status_code, 404)

    def test_uelc_admin_update_user(self):
        up = GroupUpFactory()
        url = reverse('uelcadmin-edit-user', kwargs={'pk': up.user.pk})

        request = self.client.post(
            url,
            {
                'username': 'some_random_name',
                'profile_type': up.profile_type,
                'cohort': up.cohort.pk,
            },
            HTTP_REFERER="/uelcadmin/", follow=True)
        self.assertEqual(request.status_code, 200)
        self.assertTrue(
            User.objects.filter(username='some_random_name').exists())

    def test_uelc_admin_update_user_long_username(self):
        up = GroupUpFactory()
        url = reverse('uelcadmin-edit-user', kwargs={'pk': up.user.pk})

        original_username = up.user.username
        long_username = 'some_random_name_longer_than_30_characters'
        request = self.client.post(
            url,
            {
                'username': long_username,
                'profile_type': up.profile_type,
                'cohort': up.cohort.pk,
            },
            HTTP_REFERER="/uelcadmin/",
            follow=True)
        self.assertEqual(request.status_code, 200)
        self.assertFalse(
            User.objects.filter(username=long_username).exists())
        self.assertTrue(
            User.objects.filter(username=original_username).exists())

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
            reverse('uelcadmin_edituserpass', args=(self.gu.user.pk,)),
            {
                'newPassword1': 'magic_password'
            },
            HTTP_REFERER='/uelcadmin/',
            follow=True)
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
        # Make sure this cache is cleared -- it's persistent across test runs,
        # and pagetree uses it a lot.
        cache.clear()
        self.profile = AdminUpFactory()
        self.client.login(username=self.profile.user.username, password='test')
        self.case = Case.objects.get(name='case-test')
        self.case.cohort.add(self.profile.cohort)
        # Simulate the case where there's "duplicate" CaseMaps.
        CaseMapFactory(case=self.case, user=self.profile.user)
        CaseMapFactory(case=self.case, user=self.profile.user)

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
            'name': 'cloned',
            'base_url': 'cloned',
        }, follow=True)

        self.assertEqual(r.status_code, 200)

        cloned_h = Hierarchy.objects.get(name='cloned')
        self.assertEqual(cloned_h.base_url, '/pages/cloned/')
        self.assertEqual(Case.objects.filter(hierarchy=cloned_h).count(), 1)

        orig_case = Case.objects.filter(hierarchy=self.h).first()
        cloned_case = Case.objects.filter(hierarchy=cloned_h).first()
        self.assertNotEqual(orig_case, cloned_case)
        self.assertEqual(cloned_case.name, 'cloned')
        self.assertEqual(cloned_case.description, self.case.description)
        self.assertEqual(cloned_case.cohort.count(), self.case.cohort.count())
        self.assertNotEqual(set(cloned_case.cohort.all()),
                            set(self.case.cohort.all()))

        # Assert that the cloned hierarchy has a new cohort.
        self.assertEqual(len(orig_case.cohorts), 1)
        self.assertEqual(len(cloned_case.cohorts), 1)
        self.assertNotEqual(orig_case.cohorts[0], cloned_case.cohorts[0])

        self.assertEqual(CaseMap.objects.filter(case=cloned_case).count(), 0)

        # Find the "Decision Block" defined in UELCModuleFactory. This is
        # represented by the CaseQuiz class.
        self.assertEqual(CaseQuiz.objects.count(), 2)
        casequizzes = []
        for cq in CaseQuiz.objects.all():
            if cq.pageblock().section.hierarchy == cloned_h:
                casequizzes.append(cq)

        self.assertEqual(len(casequizzes), 1)
        cq = casequizzes[0]
        self.assertEqual(cq.pageblock().section.label, 'Your First Decision')

        # Now verify that the questions and answers for this CaseQuiz
        # have been cloned accurately.
        questions = Question.objects.filter(quiz=cq)
        self.assertEqual(len(questions), 1)
        question = questions[0]

        self.assertEqual(question.text, 'Select One')
        self.assertEqual(question.question_type, 'single choice')

        answers = Answer.objects.filter(question=question)
        self.assertEqual(len(answers), 3)

        answer1 = answers.get(value=1)
        answer2 = answers.get(value=2)
        answer3 = answers.get(value=3)

        # UELC also has the special "CaseAnswer" model, which we need to
        # verify is correctly cloned.
        self.assertEqual(CaseAnswer.objects.count(), 6)
        ca = CaseAnswer.objects.get(answer=answer1)
        self.assertEqual(ca.title, 'Choice 1: Full Disclosure')
        self.assertEqual(
            ca.description,
            'You have chosen to '
            'address the allegations publicly '
            'and commence to investigate the '
            'allegations.')

        ca = CaseAnswer.objects.get(answer=answer2)
        self.assertEqual(
            ca.title,
            'Choice 2: Initiate an Unofficial Investigation')

        ca = CaseAnswer.objects.get(answer=answer3)
        self.assertEqual(
            ca.title,
            'Choice 3: Initiate an Unofficial Investigation')

        curveball_section = self.h.find_section_from_path(
            'part-1/your-first-decision/curve-ball/')
        block = curveball_section.pageblock_set.first()
        cloned_section = cloned_h.find_section_from_path(
            'part-1/your-first-decision/curve-ball/')
        cloned_block = cloned_section.pageblock_set.first()
        self.assertEqual(block.as_dict(), cloned_block.as_dict())

        decision_section = self.h.find_section_from_path(
            'part-1/your-first-decision/')
        block = decision_section.pageblock_set.first()
        cloned_section = cloned_h.find_section_from_path(
            'part-1/your-first-decision/')
        cloned_block = cloned_section.pageblock_set.first()
        self.assertEqual(block.as_dict(), cloned_block.as_dict())

        # Verify that the clone process created a new cohort attached
        # to the cloned case, with 4 users and an admin.
        self.assertEqual(len(cloned_case.cohorts), 1)
        cloned_cohort = cloned_case.cohorts[0]
        self.assertEqual(len(cloned_cohort._get_users()), 5)
        users = cloned_cohort._get_users()
        self.assertEqual(
            len(filter(lambda x: x.username == 'cloned-1', users)), 1)
        self.assertEqual(
            len(filter(lambda x: x.username == 'cloned-2', users)), 1)
        self.assertEqual(
            len(filter(lambda x: x.username == 'cloned-3', users)), 1)
        self.assertEqual(
            len(filter(lambda x: x.username == 'cloned-4', users)), 1)
        self.assertEqual(
            len(filter(lambda x: x.username == 'cloned-admin', users)), 1)

    def test_post_with_spaces_in_name(self):
        url = reverse('clone-hierarchy', kwargs={
            'hierarchy_id': self.h.pk
        })
        r = self.client.post(url, {
            'name': 'Test Case',
            'base_url': 'test-case',
        }, follow=True)

        self.assertEqual(r.status_code, 200)

        self.assertEqual(Hierarchy.objects.count(), 2)
        self.assertEqual(
            Hierarchy.objects.get(base_url='/pages/test-case/'),
            Hierarchy.objects.get(name='Test Case'))
        self.assertEqual(
            Hierarchy.objects.filter(base_url='/pages/test-case/').count(),
            1)
        self.assertEqual(
            Hierarchy.objects.filter(name='Test Case').count(),
            1)

        cloned_h = Hierarchy.objects.get(name='Test Case')
        self.assertEqual(cloned_h.base_url, '/pages/test-case/')
        self.assertEqual(Case.objects.filter(hierarchy=cloned_h).count(), 1)

        cloned_case = Case.objects.filter(hierarchy=cloned_h).first()
        self.assertEqual(cloned_case.name, 'Test Case')
        self.assertEqual(cloned_case.description, self.case.description)
        self.assertEqual(cloned_case.cohort.count(), self.case.cohort.count())
        self.assertNotEqual(set(cloned_case.cohort.all()),
                            set(self.case.cohort.all()))

    def test_post_with_name_different_than_url(self):
        url = reverse('clone-hierarchy', kwargs={
            'hierarchy_id': self.h.pk
        })
        r = self.client.post(url, {
            'name': 'Some Random Name',
            'base_url': 'my-test-case',
        }, follow=True)

        self.assertEqual(r.status_code, 200)

        self.assertEqual(Hierarchy.objects.count(), 2)
        self.assertEqual(
            Hierarchy.objects.get(base_url='/pages/my-test-case/'),
            Hierarchy.objects.get(name='Some Random Name'))
        self.assertEqual(
            Hierarchy.objects.filter(base_url='/pages/my-test-case/').count(),
            1)
        self.assertEqual(
            Hierarchy.objects.filter(name='Some Random Name').count(),
            1)

        cloned_h = Hierarchy.objects.get(name='Some Random Name')
        self.assertEqual(cloned_h.base_url, '/pages/my-test-case/')
        self.assertEqual(Case.objects.filter(hierarchy=cloned_h).count(), 1)

        cloned_case = Case.objects.filter(hierarchy=cloned_h).first()
        self.assertEqual(cloned_case.name, 'Some Random Name')
        self.assertEqual(cloned_case.description, self.case.description)
        self.assertEqual(cloned_case.cohort.count(), self.case.cohort.count())
        self.assertNotEqual(set(cloned_case.cohort.all()),
                            set(self.case.cohort.all()))

    def test_post_with_duplicate_base_url(self):
        url = reverse('clone-hierarchy', kwargs={
            'hierarchy_id': self.h.pk
        })
        r = self.client.post(url, {
            'name': 'Some Random Name',
            'base_url': self.h.base_url,
        }, follow=True)

        self.assertEqual(r.status_code, 200)

        self.assertEqual(Hierarchy.objects.count(), 1)
        self.assertContains(
            r,
            'already a hierarchy with the base_url: {}'.format(
                self.h.base_url))

        r = self.client.post(url, {
            'name': 'Some Random Name',
            'base_url': 'case-test',
        }, follow=True)

        self.assertEqual(r.status_code, 200)

        self.assertEqual(Hierarchy.objects.count(), 1)
        self.assertContains(
            r,
            'already a hierarchy with the base_url: {}'.format(
                self.h.base_url))


class UELCPageViewTest(TestCase):

    def setUp(self):
        UELCModuleFactory()
        self.h = Hierarchy.objects.get(name='case-test')

        self.view = UELCPageView()
        self.view.hierarchy_base = self.h.base_url
        self.view.hierarchy_name = self.h.name

        self.view.request = RequestFactory().get('/')
        self.setup_request(self.view.request)

    def setup_request(self, request):
        """Annotate a request object with a session"""
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        """Annotate a request object with a messages"""
        middleware = MessageMiddleware()
        middleware.process_request(request)
        request.session.save()

        request.session['some'] = 'some'
        request.session.save()

    def test_root_section_check_invalid_as_admin(self):
        view = UELCPageView()
        view.request = RequestFactory().get('/')
        view.request.user = AdminUpFactory().user
        self.setup_request(view.request)

        h = HierarchyFactory()
        s = h.get_root()

        response = view.root_section_check(s, None)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/pages/case-one/edit/')

    def test_root_section_check_invalid_as_group_user(self):
        view = UELCPageView()
        view.request = RequestFactory().get('/')
        view.request.user = GroupUpFactory().user
        self.setup_request(view.request)

        h = HierarchyFactory()
        s = h.get_root()

        response = view.root_section_check(s, None)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, view.no_root_fallback_url)

    def test_root_section_check_valid(self):
        s1 = self.h.get_root().get_first_child()
        s2 = s1.get_next()

        self.view.request.user = GroupUpFactory().user

        response = self.view.root_section_check(s1, s2)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, s2.get_absolute_url())

    def test_perform_checks_root(self):
        s = self.h.get_root()
        child = s.get_next()

        self.view.request.user = GroupUpFactory().user

        response = self.view.perform_checks(self.view.request, '/')

        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, child.get_absolute_url())

    def test_perform_checks_module(self):
        s = self.h.get_root().get_first_child().get_module()

        self.view.request.user = GroupUpFactory().user

        response = self.view.perform_checks(self.view.request, s.get_path())

        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, s.get_next().get_absolute_url())

    def test_perform_checks_not_allowed(self):
        self.view.request.user = GroupUpFactory().user

        s = self.h.get_root().get_last_child()
        response = self.view.perform_checks(self.view.request, s.get_path())

        self.assertEquals(response.status_code, 302)
        self.assertEquals(
            response.url,
            '/pages/case-test/part-2-choice-1/your-second-decision/')

    def test_perform_checks_child(self):
        self.view.request.user = GroupUpFactory().user
        self.view.request.user.is_impersonate = False

        s = self.h.get_root().get_first_leaf()
        response = self.view.perform_checks(self.view.request, s.get_path())

        self.assertEquals(response, None)
        self.assertEquals(self.view.section, s)
        self.assertEquals(self.view.root, self.h.get_root())
        self.assertEquals(self.view.module, s.get_module())
        self.assertEquals(self.view.upv.section, s)
        self.assertEquals(self.view.upv.user, self.view.request.user)


class TestFacilitatorView(TestCase):

    def setUp(self):
        UELCModuleFactory()
        self.h = Hierarchy.objects.get(name='case-test')
        self.view = FacilitatorView()

    def test_set_upv(self):
        user = GroupUpFactory().user
        section = Section.objects.get(slug='home')

        # no-op
        self.view.set_upv(user, section, 'complete')
        qs = UserPageVisit.objects.filter(user=user, section=section)
        self.assertEquals(qs.count(), 0)

        # status will be updated on existing upv
        upv = UserPageVisit.objects.create(user=user, section=section)
        self.assertEquals(upv.status, 'incomplete')

        self.view.set_upv(user, section, 'complete')
        upv.refresh_from_db()
        self.assertEquals(upv.status, 'complete')

    def test_post_curveball_select(self):
        user = GroupUpFactory().user
        section = Section.objects.filter(slug='curve-ball').first()
        blk = section.pageblock_set.all()[1].block()

        data = {
            'user_id': user.id,
            'curveball': blk.curveball_one.id,
            'curveball-block-id': blk.id,
            'curveball-select': True
        }
        self.view.request = RequestFactory().post('/', data)
        self.view.post(self.view.request, 'home/')

        qs = CurveballSubmission.objects.filter(
            curveball=blk.curveball_one, group_curveball=user,
            curveballblock=blk)
        self.assertEquals(qs.count(), 1)

    def test_post_gate_action(self):
        user = GroupUpFactory().user
        section = Section.objects.filter(slug='confirm-first-decision').first()
        upv = UserPageVisitFactory(user=user, section=section)

        data = {
            'user_id': user.id,
            'gate-action': 'submit',
            'section': section.id
        }
        self.view.request = RequestFactory().post('/', data)
        self.view.post(self.view.request, 'home/')

        upv.refresh_from_db()
        self.assertEquals(upv.status, 'complete')

        qs = GateSubmission.objects.filter(section=section)
        self.assertEquals(qs.count(), 1)

    def test_get(self):
        facilitator = FacilitatorUpFactory().user
        self.client.login(username=facilitator.username, password='test')

        case = self.h.case_set.first()
        case.cohort.add(facilitator.profile.cohort)
        group_user = GroupUpFactory()
        facilitator.profile.cohort.user_profile_cohort.add(group_user)

        section = Section.objects.filter(slug='home').first()
        url = reverse('facilitator-view',
                      kwargs={'hierarchy_name': self.h.name,
                              'path': section.get_path()})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['section'], section)
        self.assertTrue(response.context['is_facilitator_view'])
        self.assertEquals(response.context['case'], case)

        self.assertEquals(len(response.context['user_sections']), 1)
        user_sections = response.context['user_sections'][0]
        self.assertEquals(user_sections[0], group_user.user)
        self.assertEquals(user_sections[2].path, '/')

        gates = user_sections[1]
        self.assertEquals(len(gates), 5)
        self.assertEquals(gates[0][0].slug, 'your-first-decision')
        self.assertEquals(gates[1][0].slug, 'curve-ball')
        self.assertEquals(gates[2][0].slug, 'confirm-first-decision')
        self.assertEquals(gates[3][0].slug, 'discussion-of-impact')
        self.assertEquals(gates[4][0].slug, 'results')


class TestResetUserCaseProgress(TestCase):

    def set_up_alt_case(self):
        self.alt_h = HierarchyFactory(name='alt-test',
                                      base_url='/pages/alt-test/')

        self.alt_case = CaseFactory(name='alt-case-test',
                                    hierarchy=self.alt_h)

        root = self.alt_h.get_root()
        root.add_child_section_from_dict({
            'label': 'Part 1',
            'slug': 'part-1',
            'children': [
                {
                    'label': 'Your First Decision',
                    'slug': 'your-first-decision',
                    'pageblocks': [
                        {
                            'block_type': 'Decision Block',
                            'questions': [{
                                'text': 'Select One',
                                'question_type': 'single choice',
                                'answers': [
                                    {
                                        'value': '1',
                                        'title': 'Choice 1',
                                    },
                                ]
                            }],
                        },
                        {
                            'block_type': 'Gate Block',
                            'label': 'First Decision Point'
                        },
                    ],
                    'children': [{
                        'label': 'Curve Ball',
                        'slug': 'curve-ball',
                        'pageblocks': [
                            {
                                'block_type': 'Gate Block',
                                'label': 'Curveball',
                            },
                            {
                                'block_type': 'Curveball Block',
                                'label': 'alt-curveball-block-1',
                                'description': 'alt description',
                                'curveball_one': CurveballFactory(),
                                'curveball_two': CurveballFactory(),
                                'curveball_three': CurveballFactory(),
                            },
                        ],
                        'children': [{
                            'label': 'Confirm First Decision',
                            'slug': 'confirm-first-decision',
                            'pageblocks': [{
                                'block_type': 'Gate Block',
                                'label': 'Confirm First Decision',
                            }],
                        }]

                    }]
                },
            ]
        })

    def setUp(self):
        # create user1 history in primary and alt hierarchy
        # create user2 history in primary hierarchy
        # Tests will delete user1 history in primary hierarchy

        f = UELCModuleFactory()
        self.case = f.case
        self.h = self.case.hierarchy

        self.set_up_alt_case()

        self.user1 = GroupUpFactory().user
        self.user2 = GroupUpFactory().user

        self.url = reverse('reset-user-case-progress',
                           args=[self.case.id])
        self.data = {'user-id': self.user1.id}

        facilitator = FacilitatorUpFactory().user
        self.client.login(username=facilitator.username, password='test')

    def test_post_delete_case_maps(self):
        # casemaps
        cm1 = CaseMapFactory(case=self.case, user=self.user1)
        cm2 = CaseMapFactory(case=self.alt_case, user=self.user1)
        cm3 = CaseMapFactory(case=self.case, user=self.user2)

        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 302)

        with self.assertRaises(CaseMap.DoesNotExist):
            CaseMap.objects.get(id=cm1.id)

        self.assertEquals(cm2, CaseMap.objects.get(id=cm2.id))
        self.assertEquals(cm3, CaseMap.objects.get(id=cm3.id))

    def test_post_delete_user_visits(self):
        s1 = Section.objects.get(hierarchy=self.h, slug='part-1')
        alt1 = Section.objects.get(hierarchy=self.alt_h, slug='part-1')

        uv1 = UserPageVisitFactory(user=self.user1, section=s1)
        uv2 = UserPageVisitFactory(user=self.user1, section=alt1)
        uv3 = UserPageVisitFactory(user=self.user2, section=s1)

        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 302)

        with self.assertRaises(UserPageVisit.DoesNotExist):
            UserPageVisit.objects.get(id=uv1.id)

        self.assertEquals(uv2, UserPageVisit.objects.get(id=uv2.id))
        self.assertEquals(uv3, UserPageVisit.objects.get(id=uv3.id))

    def test_post_delete_user_locations(self):
        l1 = UserLocation.objects.create(user=self.user1, hierarchy=self.h)
        l2 = UserLocation.objects.create(user=self.user1, hierarchy=self.alt_h)
        l3 = UserLocation.objects.create(user=self.user2, hierarchy=self.h)

        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 302)

        with self.assertRaises(UserLocation.DoesNotExist):
            UserLocation.objects.get(id=l1.id)

        self.assertEquals(l2, UserLocation.objects.get(id=l2.id))
        self.assertEquals(l3, UserLocation.objects.get(id=l3.id))

    def test_post_delete_section_submissions(self):
        s1 = Section.objects.get(hierarchy=self.h, slug='part-1')
        alt1 = Section.objects.get(hierarchy=self.alt_h, slug='part-1')

        ss1 = SectionSubmissionFactory(user=self.user1, section=s1)
        ss2 = SectionSubmissionFactory(user=self.user1, section=alt1)
        ss3 = SectionSubmissionFactory(user=self.user2, section=s1)

        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 302)

        with self.assertRaises(SectionSubmission.DoesNotExist):
            SectionSubmission.objects.get(id=ss1.id)

        self.assertEquals(ss2, SectionSubmission.objects.get(id=ss2.id))
        self.assertEquals(ss3, SectionSubmission.objects.get(id=ss3.id))

    def test_post_delete_curveballs(self):
        cb1 = CurveballBlock.objects.get(description='curveball description 1')
        cb2 = CurveballBlock.objects.get(description='alt description')

        cs1 = CurveballSubmissionFactory(
            curveballblock=cb1, group_curveball=self.user1)
        cs2 = CurveballSubmissionFactory(
            curveballblock=cb2, group_curveball=self.user1)
        cs3 = CurveballSubmissionFactory(
            curveballblock=cb1, group_curveball=self.user2)

        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 302)

        with self.assertRaises(CurveballSubmission.DoesNotExist):
            CurveballSubmission.objects.get(id=cs1.id)

        self.assertEquals(cs2, CurveballSubmission.objects.get(id=cs2.id))
        self.assertEquals(cs3, CurveballSubmission.objects.get(id=cs3.id))

    def test_post_delete_gateblocks(self):
        ids = content_blocks_by_hierarchy_and_class(self.h, GateBlock)
        gb1 = GateBlock.objects.get(id=ids[0])

        ids = content_blocks_by_hierarchy_and_class(self.alt_h, GateBlock)
        gb2 = GateBlock.objects.get(id=ids[0])

        gs1 = GateSubmissionFactory(
            gateblock=gb1, section=gb1.pageblock().section,
            gate_user=self.user1)
        gs2 = GateSubmissionFactory(
            gateblock=gb2, section=gb2.pageblock().section,
            gate_user=self.user1)
        gs3 = GateSubmissionFactory(
            gateblock=gb1, section=gb1.pageblock().section,
            gate_user=self.user2)

        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 302)

        with self.assertRaises(GateSubmission.DoesNotExist):
            GateSubmission.objects.get(id=gs1.id)

        self.assertEquals(gs2, GateSubmission.objects.get(id=gs2.id))
        self.assertEquals(gs3, GateSubmission.objects.get(id=gs3.id))
