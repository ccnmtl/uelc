from django.test import TestCase
from django.test.client import Client
from pagetree.helpers import get_hierarchy
from django.contrib.auth.models import User
from factories import GroupUpFactory, AdminUpFactory, \
    CaseFactory, CohortFactory
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
        assert "PASS" in response.content


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
        self.u = User.objects.create(username="testuser")
        self.u.set_password("test")
        self.u.save()
        self.c.login(username="testuser", password="test")

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

        self.grp_usr = GroupUpFactory().user
        self.client = Client()
        self.client.login(username=self.grp_usr.username, password="test")

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


class TestAdminViews(TestCase):

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
