from django.test import TestCase
from .factories import (
    CohortFactory, UserProfileFactory, CaseFactory, CaseMapFactory,
    TextBlockDTFactory, UELCHandlerFactory, LibraryItemFactory)
from uelc.main.models import TextBlockDT, LibraryItem


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


class DummySection(object):
    def get_tree(self):
        return [self]


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

    def test_get_vals_from_casemap(self):
        u = UELCHandlerFactory()
        self.assertEqual(u.get_vals_from_casemap([1]), [1])
        self.assertEqual(u.get_vals_from_casemap([0, 2, 3]), [2, 3])

    def test_get_partchoice_by_username(self):
        class DummyUserMap(object):
            value = [1]

        u = UELCHandlerFactory()
        self.assertEqual(u.get_partchoice_by_usermap(DummyUserMap()), 1)

        d = DummyUserMap()
        d.value = [9, 3]
        r = u.get_partchoice_by_usermap(d)
        self.assertTrue(2.29 < r < 2.31)

    def test_get_p1c1(self):
        u = UELCHandlerFactory()
        self.assertEqual(u.get_p1c1([1, 2]), 2)

    def test_can_show_empty(self):
        u = UELCHandlerFactory()
        r = u.can_show(None, DummySection(), [])
        self.assertEqual(r, 0)

    def test_can_show(self):
        u = UELCHandlerFactory()
        r = u.can_show(None, DummySection(), [7])
        self.assertEqual(r, 7)

    def test_p1pre(self):
        u = UELCHandlerFactory()
        self.assertEqual(u.p1pre([]), 0)
        self.assertEqual(u.p1pre([1]), 0)
        self.assertEqual(u.p1pre([1, 2]), 1)


class LibraryItemTest(TestCase):
    def test_unicode(self):
        i = LibraryItemFactory()
        self.assertEqual(str(i), i.name)

    def test_get_users(self):
        i = LibraryItemFactory()
        self.assertEqual(i.get_users().count(), 0)

    def test_add_form(self):
        f = LibraryItem.add_form()
        self.assertTrue('name' in f.fields)

    def test_edit_form(self):
        i = LibraryItemFactory()
        self.assertTrue('name' in i.edit_form().fields)
