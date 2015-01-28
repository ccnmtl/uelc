from django.test import TestCase
#from django.core.exceptions import ValidationError
from uelc.main.tests.factories import (
    UserFactory, AdminUserFactory,
    FacilitatorUserFactory, GroupnUserFactory,
    CaseFactory, CohortFactory, LibraryItemFactory,)
#from nose.tools import set_trace


class BasicModelTest(TestCase):

    def setup(self):
        self.user = UserFactory()


class TestAdminUser(TestCase):

    def test_unicode(self):
        userprofile = AdminUserFactory()
        self.assertEqual(userprofile.display_name(),
                         userprofile.user.first_name)
        self.assertTrue(userprofile.is_admin())


class TestFacilitatorUser(TestCase):

    def test_unicode(self):
        userprofile = FacilitatorUserFactory()
        self.assertEqual(userprofile.display_name(),
                         userprofile.user.first_name)
        self.assertTrue(userprofile.is_assistant())


class TestGroupUser(TestCase):

    def test_unicode(self):
        userprofile = GroupnUserFactory()
        self.assertEqual(userprofile.display_name(),
                         userprofile.user.first_name)
        self.assertTrue(userprofile.is_group_user())


class TestCohort(TestCase):

    def test_unicode(self):
        user = UserFactory()
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
