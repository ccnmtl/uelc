from django.test import TestCase
# from django.test.client import Client
from pagetree.helpers import get_hierarchy
from factories import GroupUpFactory, HierarchyFactory
from quizblock.tests.test_models import FakeReq
# from pagetree.tests.factories import ModuleFactory
# from quizblock.tests.test_models import FakeReq
from gate_block.models import GateBlock
from uelc.main.models import CaseQuiz
from uelc.main.helper_functions import (
    admin_ajax_page_submit, admin_ajax_reset_page)


class TestHelperFunctions(TestCase):

    def setUp(self):
        self.hierarchy = HierarchyFactory(name="main", base_url="/pages/main/")
        self.root = self.hierarchy.get_root()
        self.r = FakeReq()
        self.r.POST = {'description': 'description', 'rhetorical': False,
                  'allow_redo': True, 'show_submit_state': False}
        self.casequiz = CaseQuiz.create(self.r)
        self.root.add_pageblock_from_dict(self.casequiz.as_dict())
        self.section = self.hierarchy.get_root().get_first_leaf()
        self.section.add_pageblock_from_dict(self.casequiz.as_dict())
        self.section.append_pageblock('', '', self.casequiz)
        self.gate_block = GateBlock.objects.create()
        self.section.append_pageblock('', '', self.gate_block)
        self.grp_usr_profile = GroupUpFactory()

    def test_admin_ajax_page_submit(self):
        '''There are two unlock methods - one in CaseQuiz and another in GateBlock do we need both?
        Guess I'll test both....'''
        # from nose.tools import set_trace
        # set_trace()
        # self.casequiz
        # self.assertFalse(self.section.unlocked())
        self.assertFalse(self.gate_block.unlocked(self.grp_usr_profile.user, self.section))
        """admin_ajax_page_submit(section, user)"""
        admin_ajax_page_submit(self.section, self.grp_usr_profile.user)
        '''This line keeps throwing errors the function signature for
        GateBlock unlocked is unlocked(self, user, section): and calling
        admin_ajax_page_submit should be creating a submission object for the user'''
        self.assertTrue(self.gate_block.unlocked(self.grp_usr_profile.user, self.section))

    def test_admin_ajax_reset_page(self):
        pass
#         self.assertTrue(self.section.unlocked(self.grp_usr_profile.user))
#         admin_ajax_reset_page(self.section, self.grp_usr_profile.user)
#         self.assertFalse(self.section.unlocked(self.grp_usr_profile.user))

    def test_page_submit(self):
        pass

    def test_reset_page(self):
        pass

    def test_get_root_context(self):
        pass

    def test_has_responses(self):
        pass
