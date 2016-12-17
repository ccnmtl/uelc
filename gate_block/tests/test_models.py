from django.test import TestCase
from pagetree.helpers import get_hierarchy
from pagetree.models import Section, UserLocation
from pagetree.tests.factories import ModuleFactory, UserPageVisitFactory
from quizblock.models import Submission
from quizblock.tests.test_models import FakeReq

from gate_block.models import GateBlock
from gate_block.tests.factories import (
    SectionSubmissionFactory, GateSubmissionFactory,
    GroupUserFactory, GateBlockFactory)
from uelc.main.tests.factories import GroupUpFactory, UELCModuleFactory


class GateBlockTest(TestCase):
    def setUp(self):
        self.gbf = GateBlockFactory()

    def test_add_form(self):
        f = GateBlock.add_form()
        self.assertEqual(None, f.full_clean())

    def test_edit_form(self):
        f = self.gbf.edit_form()
        self.assertEqual(None, f.full_clean())

    def test_edit(self):
        self.gbf.edit(None, None)

    def test_redirect_to_self_on_submit(self):
        self.assertTrue(self.gbf.redirect_to_self_on_submit())

    def test_needs_submit(self):
        self.assertTrue(self.gbf.needs_submit())

    def test_allow_redo(self):
        self.assertFalse(self.gbf.allow_redo())

    def test_unlocked_false(self):
        u = GroupUserFactory()
        self.assertFalse(self.gbf.unlocked(u, None))


class TestGateBlockStatus(TestCase):

    def setUp(self):
        f = UELCModuleFactory()
        self.h = f.root.hierarchy
        self.group_user = GroupUpFactory().user
        self.uloc = UserLocation.objects.create(user=self.group_user,
                                                hierarchy=self.h)
        self.section = Section.objects.get(slug='your-first-decision')
        self.pageblocks = self.section.pageblock_set.all()
        self.gate_block = self.section.pageblock_set.filter(
            content_type__model='gateblock').first().block()

    def test_status_to_be_reviewed(self):
        status = self.gate_block.status(
            self.group_user, self.uloc, False, self.pageblocks)
        self.assertEquals(status, 'to be reviewed')

    def test_status_paths_match(self):
        self.uloc.path = self.section.get_path()
        self.uloc.save()

        status = self.gate_block.status(
            self.group_user, self.uloc, False, self.pageblocks)
        self.assertEquals(status, 'reviewing')

    def test_status_user_page_visited(self):
        UserPageVisitFactory(user=self.group_user, section=self.section)
        status = self.gate_block.status(
            self.group_user, self.uloc, False, self.pageblocks)
        self.assertEquals(status, 'reviewing')

    def test_status_gate_submitted(self):
        status = self.gate_block.status(
            self.group_user, self.uloc, True, self.pageblocks)
        self.assertEquals(status, 'reviewed')

    def test_status_decision_block_submitted(self):
        decision_block = self.section.pageblock_set.filter(
            content_type__model='casequiz').first().block()
        Submission.objects.create(quiz=decision_block, user=self.group_user)
        status = self.gate_block.status(
            self.group_user, self.uloc, False, self.pageblocks)
        self.assertEquals(status, 'reviewed')

    def test_status_section_submission_exists(self):
        SectionSubmissionFactory(section=self.section,
                                 user=self.group_user,
                                 submitted=True)
        status = self.gate_block.status(
            self.group_user, self.uloc, False, self.pageblocks)
        self.assertEquals(status, 'reviewed')


class CreateGateBlockTest(TestCase):

    def setUp(self):
        self.fake_req = FakeReq()

    def test_create(self):
        newgb = GateBlock.create(self.fake_req)
        self.assertEqual(type(newgb), GateBlock)


class GateSubmissionTest(TestCase):
    def setUp(self):
        ModuleFactory("main", "/pages/main/")
        self.hierarchy = get_hierarchy(name='main')
        self.section = self.hierarchy.get_root().get_first_leaf()
        self.gbf = GateBlockFactory()
        self.gu = GroupUserFactory()
        self.gs = GateSubmissionFactory(
            gate_user=self.gu, section=self.section, gateblock=self.gbf)

    def test_unicode(self):
        self.assertIn(unicode(self.gs.gateblock.id), str(self.gs))

    def test_unlocked_true(self):
        self.assertTrue(self.gbf.unlocked(self.gu, self.section))


class SectionSubmissionTest(TestCase):
    def setUp(self):
        ModuleFactory("main", "/pages/main/")
        self.hierarchy = get_hierarchy(name='main')
        self.section = self.hierarchy.get_root().get_first_leaf()
        self.ss = SectionSubmissionFactory(section=self.section)

    def test_unicode(self):
        self.assertIn(unicode(self.ss.section.id), str(self.ss))
