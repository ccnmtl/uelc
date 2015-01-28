from django.contrib.auth.models import User
from pagetree.models import Hierarchy
from uelc.main.models import UserProfile, Case, Cohort, LibraryItem
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


class CohortFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Cohort
    name = 'main cohort'


class HierarchyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Hierarchy
    base_url = "/"
    name = "main"


class CaseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Case
    hierarchy = factory.SubFactory(HierarchyFactory)
    cohort = factory.SubFactory(CohortFactory)
    name = "main case"


class LibraryItemFactory(factory.DjangoModelFactory):
    FACTORY_FOR = LibraryItem
    name = 'file1'
