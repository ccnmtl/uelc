from django.test import TestCase
from .factories import (
    CohortFactory, UserProfileFactory, CaseFactory, CaseMapFactory,
    TextBlockDTFactory, UELCHandlerFactory)
from uelc.main.models import TextBlockDT


class CohortTest(TestCase):
    def test_unicode(self):
        c = CohortFactory()
        self.assertTrue(str(c).startswith("cohort "))


class UserProfileTest(TestCase):
    def test_cohorts(self):
        up = UserProfileFactory()
        self.assertEqual(up.cohorts, "")

    def test_unicode(self):
        up = UserProfileFactory()
        self.assertTrue(str(up).startswith("user"))


class CaseTest(TestCase):
    def test_unicode(self):
        c = CaseFactory()
        self.assertTrue(str(c).startswith("case "))


class CaseMapTest(TestCase):
    def test_get_value(self):
        cm = CaseMapFactory()
        self.assertEqual(cm.get_value(), "")

    def test_add_value_places_noop(self):
        cm = CaseMapFactory()
        cm.add_value_places(0)


class TextBlockDTTest(TestCase):
    def test_add_form(self):
        f = TextBlockDT.add_form()
        self.assertTrue('body' in f.fields)

    def test_edit_form(self):
        t = TextBlockDTFactory()
        self.assertTrue('body' in t.edit_form().fields)

    def test_save(self):
        t = TextBlockDTFactory()
        vals = dict(body="a new body",
                    after_decision="new after decision",
                    choice="new choice")
        t.edit(vals, None)
        self.assertEqual(t.body, "a new body")
        self.assertEqual(t.after_decision, "new after decision")
        self.assertEqual(t.choice, "new choice")

    def test_summary_render_short(self):
        t = TextBlockDTFactory(body="a body <>")
        self.assertEqual(t.summary_render(), "a body &lt;>")

    def test_summary_render_long(self):
        t = TextBlockDTFactory(body="foo" * 100)
        self.assertTrue(t.summary_render().endswith("..."))


class UELCHandlerTest(TestCase):
    def test_populate_map_obj_empty(self):
        u = UELCHandlerFactory()
        # have to be careful to explicitly reset map_obj
        # see PMT #99062
        u.map_obj = {}
        u.populate_map_obj([])
        self.assertEqual(u.map_obj, {})

    def test_populate_map_obj(self):
        u = UELCHandlerFactory()
        # have to be careful to explicitly reset map_obj
        # see PMT #99062
        u.map_obj = {}
        u.populate_map_obj([1, 2, 3])
        self.assertEqual(
            u.map_obj,
            {'p1c1': {'tree_index': 1, 'value': 2},
             'p1pre': {'tree_index': 0, 'value': 1},
             'p2pre': {'tree_index': 2, 'value': 3}})
