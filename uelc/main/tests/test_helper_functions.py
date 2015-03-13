from django.test import TestCase
# from django.test.client import Client
from pagetree.helpers import get_hierarchy
from factories import GroupUpFactory, UELCModuleFactory
# from pagetree.tests.factories import ModuleFactory
# from quizblock.tests.test_models import FakeReq
# from uelc.main.models import CaseQuiz
from uelc.main.helper_functions import (
    admin_ajax_page_submit, admin_ajax_reset_page)


class TestHelperFunctions(TestCase):

    def setUp(self):
        UELCModuleFactory("main", "/pages/main/")
        self.hierarchy = get_hierarchy(name='main')
        self.section = self.hierarchy.get_root().get_first_leaf()
        self.grp_usr_profile = GroupUpFactory()

    def test_admin_ajax_page_submit(self):
        '''Prior to running method it should be false no?'''
        # self.assertFalse(self.section.unlocked(self.grp_usr_profile.user))
        admin_ajax_page_submit(self.section, self.grp_usr_profile.user)
        self.assertTrue(self.section.unlocked(self.grp_usr_profile.user))

    def test_admin_ajax_reset_page(self):
        self.assertTrue(self.section.unlocked(self.grp_usr_profile.user))
        admin_ajax_reset_page(self.section, self.grp_usr_profile.user)
        # self.assertFalse(self.section.unlocked(self.grp_usr_profile.user))

    def test_page_submit(self):
        pass

    def test_reset_page(self):
        pass

    def test_get_root_context(self):
        pass

    def test_has_responses(self):
        pass
