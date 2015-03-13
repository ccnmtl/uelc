from django.test import TestCase
from factories import GroupUpFactory, HierarchyFactory
from quizblock.tests.test_models import FakeReq
from gate_block.models import GateBlock
from uelc.main.models import CaseQuiz
from uelc.main.helper_functions import (
    admin_ajax_page_submit, admin_ajax_reset_page,
    page_submit, reset_page)


class TestGateBlockandCaseQuizUnlockedFunctions(TestCase):

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
        '''There are two unlock methods - one in
        CaseQuiz and another in GateBlock'''
        self.assertFalse(
            self.gate_block.unlocked(self.grp_usr_profile.user, self.section))
        self.assertFalse(
            self.casequiz.unlocked(self.grp_usr_profile.user, self.section))
        admin_ajax_page_submit(self.section, self.grp_usr_profile.user)
        '''To test CaseQuiz unlocked we need to create a user visit...'''
        self.assertTrue(
            self.gate_block.unlocked(self.grp_usr_profile.user, self.section))

    def test_admin_ajax_reset_page(self):
        admin_ajax_page_submit(self.section, self.grp_usr_profile.user)
        self.assertTrue(
            self.gate_block.unlocked(self.grp_usr_profile.user, self.section))
        admin_ajax_reset_page(self.section, self.grp_usr_profile.user)
        self.assertFalse(self.gate_block.unlocked(
            self.grp_usr_profile.user, self.section))

    def test_reset_page(self):
        self.otr = FakeReq()
        self.otr.user = self.grp_usr_profile.user
        admin_ajax_page_submit(self.section, self.grp_usr_profile.user)
        reset_page(self.section, self.otr)
        self.assertFalse(
            self.gate_block.unlocked(self.grp_usr_profile.user, self.section))


class TestPageSubmitFunctions(TestCase):

    def setUp(self):
        self.hierarchy = HierarchyFactory(name="main", base_url="/pages/main/")
        self.root = self.hierarchy.get_root()
        self.root.add_child_section_from_dict(
            {'label': "One", 'slug': "one",
             'children': [{'label': "Three", 'slug': "introduction"}]})
        self.root.add_child_section_from_dict({'label': "Two", 'slug': "two"})
        blocks = [{'label': 'Welcome UELC',
                   'css_extra': '',
                   'block_type': 'Test Block',
                   'body': 'You should now use the edit link to add content'}]
        self.root.add_child_section_from_dict({'label': 'Four', 'slug': 'four',
                                               'pageblocks': blocks})
        self.section = self.root.get_first_child()
        self.last_section = self.root.get_last_child()
        self.otr = FakeReq()
        self.otr.POST = {'description': 'description', 'rhetorical': False,
                         'allow_redo': True, 'show_submit_state': False}
        self.grp_usr_profile = GroupUpFactory()
        self.otr.user = self.grp_usr_profile.user

    def test_page_submit(self):
        # from nose.tools import set_trace
        # set_trace()
        self.first_request = page_submit(self.section, self.otr)
        self.assertEqual(
            self.first_request['Location'],
            self.section.get_next().get_absolute_url())
        self.last_request = page_submit(self.last_section, self.otr)
        self.assertEqual(
            self.last_request['Location'],
            self.last_section.get_absolute_url())

    def test_get_root_context(self):
        pass

    def test_has_responses(self):
        pass
