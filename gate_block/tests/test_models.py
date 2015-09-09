from django.test import TestCase
from quizblock.tests.test_models import FakeReq
from gate_block.models import GateBlock
from uelc.main.tests.factories import GroupUserFactory


class GateBlockTest(TestCase):
    def test_add_form(self):
        f = GateBlock.add_form()
        self.assertEqual(None, f.full_clean())

    def test_edit_form(self):
        tb = GateBlock.objects.create()
        f = tb.edit_form()
        self.assertEqual(None, f.full_clean())

    def test_edit(self):
        tb = GateBlock.objects.create()
        tb.edit(None, None)

    def test_redirect_to_self_on_submit(self):
        tb = GateBlock.objects.create()
        self.assertTrue(tb.redirect_to_self_on_submit())

    def test_needs_submit(self):
        tb = GateBlock.objects.create()
        self.assertTrue(tb.needs_submit())

    def test_allow_redo(self):
        tb = GateBlock.objects.create()
        self.assertFalse(tb.allow_redo())

    def test_unlocked(self):
        tb = GateBlock.objects.create()
        u = GroupUserFactory()
        self.assertFalse(tb.unlocked(u, None))


class CreateGateBlockTest(TestCase):

    def setUp(self):
        self.fake_req = FakeReq()

    def test_create(self):
        newgb = GateBlock.create(self.fake_req)
        self.assertEqual(type(newgb), GateBlock)
