import factory
from django.contrib.auth.models import User

from pagetree.models import Hierarchy

from uelc.main.models import (
    Cohort, UserProfile, Case, CaseMap, TextBlockDT, UELCHandler,
    LibraryItem, CaseQuiz)


class CohortFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Cohort
    name = factory.Sequence(lambda n: "cohort %03d" % n)


class AdminUserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%03d" % n)
    is_superuser = True
    first_name = 'admin user'
    password = factory.PostGenerationMethodCall('set_password', 'test')


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
    cohort = factory.SubFactory(CohortFactory)
    profile_type = 'admin'


class FacilitatorUpFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserProfile
    user = factory.SubFactory(FacilitatorUserFactory)
    cohort = factory.SubFactory(CohortFactory)
    profile_type = 'assistant'


class GroupUpFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserProfile
    user = factory.SubFactory(GroupUserFactory)
    cohort = factory.SubFactory(CohortFactory)
    profile_type = 'group_user'


class HierarchyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Hierarchy
    base_url = "/"
    name = "main"


class CaseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Case
    name = factory.Sequence(lambda n: "case %03d" % n)
    hierarchy = factory.SubFactory(HierarchyFactory)


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
