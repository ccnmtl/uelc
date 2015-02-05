from django.contrib.auth.models import User
from pagetree.models import Hierarchy
from uelc.main.models import (
    Cohort, UserProfile, Case, CaseMap, TextBlockDT, UELCHandler,
    LibraryItem, CaseQuiz)
import factory
#from nose.tools import set_trace


class AdminUserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%03d" % n)
    is_staff = True
    first_name = 'admin user'


class FacilitatorUserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%03d" % n)
    is_staff = False
    first_name = 'facilitator user'


class GroupUserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%03d" % n)
    is_staff = False
    first_name = 'group user'


class AdminUpFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserProfile
    user = factory.SubFactory(AdminUserFactory)
    profile_type = 'admin'


class FacilitatorUpFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserProfile
    user = factory.SubFactory(FacilitatorUserFactory)
    profile_type = 'assistant'


class GroupUpFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserProfile
    user = factory.SubFactory(GroupUserFactory)
    profile_type = 'group_user'


class HierarchyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Hierarchy
    base_url = "/"
    name = "main"


class CohortFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Cohort
    name = factory.Sequence(lambda n: "cohort %03d" % n)


class CaseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Case
    name = factory.Sequence(lambda n: "case %03d" % n)
    hierarchy = factory.SubFactory(HierarchyFactory)
    cohort = factory.SubFactory(CohortFactory)


class CaseMapFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CaseMap
    case = factory.SubFactory(CaseFactory)
    user = factory.SubFactory(GroupUserFactory)


class CaseQuizFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CaseQuiz


class TextBlockDTFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TextBlockDT


class UELCHandlerFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UELCHandler
    depth = 1
    hierarchy = factory.SubFactory(HierarchyFactory)


class LibraryItemFactory(factory.DjangoModelFactory):
    FACTORY_FOR = LibraryItem
    name = factory.Sequence(lambda n: "item %03d" % n)
    case = factory.SubFactory(CaseFactory)
