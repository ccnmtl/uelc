from django.contrib.auth.models import User
from pagetree.models import Hierarchy
from uelc.main.models import (
    Cohort, UserProfile, Case, CaseMap, TextBlockDT, UELCHandler)
import factory


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%03d" % n)
    is_staff = True


class HierarchyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Hierarchy
    base_url = "/"
    name = "main"


class CohortFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Cohort
    name = factory.Sequence(lambda n: "cohort %03d" % n)


class UserProfileFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserProfile
    user = factory.SubFactory(UserFactory)
    profile_type = "admin"


class CaseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Case
    name = factory.Sequence(lambda n: "case %03d" % n)
    hierarchy = factory.SubFactory(HierarchyFactory)
    cohort = factory.SubFactory(CohortFactory)


class CaseMapFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CaseMap
    case = factory.SubFactory(CaseFactory)
    user = factory.SubFactory(UserFactory)


class TextBlockDTFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TextBlockDT


class UELCHandlerFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UELCHandler
    depth = 1
    hierarchy = factory.SubFactory(HierarchyFactory)
