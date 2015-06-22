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


class CurveballSubmissionTest(TestCase):
    def setUp(self):
        self.c = CurveballSubmissionFactory()

    def test_is_valid_from_factory(self):
        self.c.full_clean()
