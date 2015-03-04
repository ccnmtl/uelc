from django.test import TestCase
from django.test.client import Client
from pagetree.helpers import get_hierarchy
from django.contrib.auth.models import User
from pagetree.tests.factories import ModuleFactory
from uelc.main.models import UserProfile


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
        self.assertEqual(r.status_code, 200)


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
        UserProfile.objects.create(user=self.u, profile_type='group_user')
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
        self.grp_usr = User.objects.create(username="testuser")
        UserProfile.objects.create(
            user=self.grp_usr,
            profile_type='group_user')
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
