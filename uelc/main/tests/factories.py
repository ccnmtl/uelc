from django.contrib.auth.models import User
from pagetree.models import Hierarchy
from uelc.main.models import UserProfile, Case, Cohort, LibraryItem
import factory
#from nose.tools import set_trace


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%03d" % n)
    is_staff = True
    first_name = 'test user'


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
    name = "main case"


class AdminUserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserProfile
    user = factory.SubFactory(UserFactory)
    profile_type = 'admin'


class FacilitatorUserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserProfile
    user = factory.SubFactory(UserFactory)
    profile_type = 'assistant'


class GroupnUserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserProfile
    user = factory.SubFactory(UserFactory)
    profile_type = 'group_user'


class LibraryItemFactory(factory.DjangoModelFactory):
    FACTORY_FOR = LibraryItem
    name = 'file1'
