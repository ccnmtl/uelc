from django.test import TestCase
from quizblock.tests.test_models import FakeReq
from pagetree.helpers import get_hierarchy
from gate_block.models import GateBlock
from gate_block.tests.factories import (
    SectionSubmissionFactory, GateSubmissionFactory,
    GroupUserFactory, GateBlockFactory)
from pagetree.tests.factories import ModuleFactory


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
