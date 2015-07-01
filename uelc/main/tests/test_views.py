import json
from django.test import TestCase
from django.test.client import Client
from pagetree.helpers import get_hierarchy

from factories import (
    GroupUpFactory, AdminUpFactory,
    CaseFactory, CohortFactory, FacilitatorUpFactory,
    UELCModuleFactory, HierarchyFactory
)
from pagetree.models import Section
from pagetree.tests.factories import ModuleFactory


class BasicTest(TestCase):
    def setUp(self):
        self.c = Client()

    def test_root(self):
        response = self.c.get("/")
        self.assertEquals(response.status_code, 200)

    def test_smoketest(self):
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)


class PagetreeViewTestsLoggedOut(TestCase):
    def setUp(self):
        self.c = Client()
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
        self.c = Client()
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
        self.c.login(
            username=self.grp_usr_profile.user.username,
            password="test")

    def test_page(self):
        r = self.c.get("/pages/main/section-1/")
        self.assertEqual(r.status_code, 200)

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
        self.client = Client()
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
        self.client = Client()
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
        self.client = Client()
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
        request = self.client.post(
            "/uelcadmin/createuser/",
            {'username': 'NewUser', 'password1': 'magic_password',
             'user_profile': 'assistant', 'cohort': str(self.cohort.id)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_REFERER="/uelcadmin/")
        self.assertEqual(request.status_code, 302)

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


class TestAdminErrorHandlingInCaseViews(TestCase):

    def setUp(self):
        self.client = Client()
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
        tmp_stg = 'Case already exists! A case has already' + \
            '                      been created that is attached to the' + \
            '                      selected hierarchy. Do you need to create' + \
            '                      another hierarchy or should you use' + \
            '                      an existing case?'
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
        self.client = Client()
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
        self.client = Client()
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
