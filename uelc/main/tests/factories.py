import factory
from django.contrib.auth.models import User

from pagetree.models import Hierarchy
from quizblock.tests.test_models import FakeReq

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


class UELCModuleFactory(object):
    '''Stealing module factory from pagetree factories to adapt for
    casequiz tests'''
    def __init__(self, hname, base_url):
        hierarchy = HierarchyFactory(name=hname, base_url=base_url)
        root = hierarchy.get_root()
        root.add_child_section_from_dict(
            {'label': "One", 'slug': "one",
             'children': [{'label': "Three", 'slug': "introduction"}]})
        root.add_child_section_from_dict({'label': "Two", 'slug': "two"})
  
        r = FakeReq()
        r.POST = {'description': 'description', 'rhetorical': 'rhetorical',
                  'allow_redo': True, 'show_submit_state': False}
        casequiz = CaseQuiz.create(r)
        blocks = [{'label': 'Welcome to your new Forest Site',
                   'css_extra': '',
                   'block_type': 'Test Block',
                   'body': 'You should now use the edit link to add content'}]
        root.add_child_section_from_dict({'label': 'Four', 'slug': 'four',
                                          'pageblocks': blocks})
        root.add_child_section_from_dict(casequiz.as_dict())
        self.root = root

class UELCCaseQuizModuleFactory(object):
    '''Stealing module factory from pagetree factories to adapt for
    casequiz tests'''
    def __init__(self, hname, base_url):
        hierarchy = HierarchyFactory(name=hname, base_url=base_url)
        root = hierarchy.get_root()
        root.add_child_section_from_dict(
            {'label': "One", 'slug': "one",
             'children': [{'label': "Three", 'slug': "introduction"}]})
        root.add_child_section_from_dict({'label': "Two", 'slug': "two"})
  
        r = FakeReq()
        r.POST = {'description': 'description', 'rhetorical': 'rhetorical',
                  'allow_redo': True, 'show_submit_state': False}
        casequiz = CaseQuiz.create(r)
        blocks = [{'label': 'Welcome to your new Forest Site',
                   'css_extra': '',
                   'block_type': 'Test Block',
                   'body': 'You should now use the edit link to add content'}]
        root.add_child_section_from_dict({'label': 'Four', 'slug': 'four',
                                          'pageblocks': blocks})
        root.add_child_section_from_dict(casequiz.as_dict())
        self.root = root