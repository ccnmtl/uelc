import json
from django.test import TestCase
from curveball.tests.factories import (
    CurveballFactory, CurveballBlockFactory, CurveballSubmissionFactory
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


class CurveballSubmissionTest(TestCase):
    def setUp(self):
        self.c = CurveballSubmissionFactory()

    def test_is_valid_from_factory(self):
        self.c.full_clean()
