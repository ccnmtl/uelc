import json
from django.test import TestCase
from quizblock.tests.test_models import FakeReq
from curveball.models import CurveballBlock
from curveball.tests.factories import (
    CurveballFactory, CurveballBlockFactory, CurveballSubmissionFactory,
    GroupUserFactory
)


class CurveballTest(TestCase):
    def setUp(self):
        self.c = CurveballFactory()

    def test_is_valid_from_factory(self):
        self.c.full_clean()

    def test_is_json_serializable(self):
        json.dumps(self.c.as_dict())


class CurveballBlockTest(TestCase):
    def setUp(self):
        self.c = CurveballBlockFactory()

    def test_is_valid_from_factory(self):
        self.c.full_clean()

    def test_is_json_serializable(self):
        json.dumps(self.c.as_dict())

    def test_redirect_on_submit(self):
        self.assertFalse(self.c.redirect_to_self_on_submit())

    def test_needs_submit(self):
        self.assertTrue(self.c.needs_submit())

    def test_allow_redo(self):
        self.assertFalse(self.c.allow_redo())

    def test_edit_form(self):
        f = self.c.edit_form()
        self.assertEqual(None, f.full_clean())

    def test_get_curveballs(self):
        curveballs = self.c.get_curveballs()
        self.assertEqual(curveballs[0], self.c.curveball_one)
        self.assertEqual(curveballs[1], self.c.curveball_two)
        self.assertEqual(curveballs[2], self.c.curveball_three)

    def test_get_latest_curveball_submission_none(self):
        self.gu = GroupUserFactory()
        cbsub = self.c.get_latest_curveball_submission(self.gu)
        self.assertIsNone(cbsub)

    def test_create_submission_and_latest_curveball(self):
        self.gu = GroupUserFactory()
        self.c.create_submission(self.gu, self.c.curveball_one)
        cbsub = self.c.get_latest_curveball_submission(self.gu)
        self.assertIsNotNone(cbsub)


class CurveballSubmissionTest(TestCase):
    def setUp(self):
        self.cs = CurveballSubmissionFactory()

    def test_is_valid_from_factory(self):
        self.cs.full_clean()


class CreateCurveballTest(TestCase):

    def setUp(self):
        self.fake_req = FakeReq()

    def test_create(self):
        newcb = CurveballBlock.create(self.fake_req)
        self.assertEqual(type(newcb), CurveballBlock)


class UserCurveballInteractionTest(TestCase):

    def setUp(self):
        self.gu = GroupUserFactory()
        self.cbb = CurveballBlockFactory()
        self.cs = CurveballSubmissionFactory(curveballblock=self.cbb,
                                             group_curveball=self.gu,
                                             curveball=self.cbb.curveball_one)

    def test_get_latest_curveball_submission_not_none(self):
        cbsub = self.cbb.get_latest_curveball_submission(self.gu)
        self.assertEqual(cbsub, self.cs)
