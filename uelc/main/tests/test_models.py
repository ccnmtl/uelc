from django.test import TestCase
#from django.core.exceptions import ValidationError
from uelc.main.tests.factories import (
    AdminUserFactory, AdminUpFactory, FacilitatorUpFactory,
    GroupUserFactory, GroupUpFactory, CaseFactory,
    CohortFactory, LibraryItemFactory)
#from nose.tools import set_trace


class BasicModelTest(TestCase):

    def setup(self):
        self.user = AdminUserFactory()


class TestAdminUp(TestCase):

    def test_unicode(self):
        upro = AdminUpFactory()
        self.assertEqual(upro.display_name(),
                         upro.user.first_name)
        self.assertTrue(upro.is_admin())


class TestFacilitatorUp(TestCase):

    def test_unicode(self):
        upro = FacilitatorUpFactory()
        self.assertEqual(upro.display_name(),
                         upro.user.first_name)
        self.assertTrue(upro.is_assistant())


class TestGroupUp(TestCase):

    def test_unicode(self):
        upro = GroupUpFactory()
        self.assertEqual(upro.display_name(),
                         upro.user.first_name)
        self.assertTrue(upro.is_group_user())


class TestCohort(TestCase):

    def test_unicode(self):
        user = GroupUserFactory()
        cohort = CohortFactory()
        cohort.user.add(user)
        self.assertEqual(cohort.display_name(), cohort.name)


class TestUELCCase(TestCase):

    def test_unicode(self):
        case = CaseFactory()
        self.assertEqual(case.display_name(), case.name)


class TestLibraryItem(TestCase):

    def test_unicode(self):
        li = LibraryItemFactory(case=CaseFactory())
        self.assertEqual(li.display_name(), li.name)
