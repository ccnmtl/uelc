import factory
from django.contrib.auth.models import User

from pagetree.models import Hierarchy
from quizblock.models import Quiz, Question

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


class QuizFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Quiz


class CaseQuizFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CaseQuiz


class QuestionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Question


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
    """
    A factory for creating a production-like tree of Sections/Pageblocks
    for testing UELC.
    """
    def __init__(self, hname='main', base_url='/pages/'):
        hierarchy = HierarchyFactory(name=hname, base_url=base_url)
        root = hierarchy.get_root()
        root.add_child_section_from_dict({
            'label': 'Part 1',
            'slug': 'part-1',
            'children': [
                {
                    'label': 'Home',
                    'slug': 'home',
                    'pageblocks': [],
                },
                {
                    'label': 'Intro',
                    'slug': 'intro',
                    'pageblocks': [],
                },
                {
                    'label': 'Challenges',
                    'slug': 'challenges',
                    'pageblocks': [],
                },
                {
                    'label': 'The Superintendent',
                    'slug': 'the-superintendent',
                    'pageblocks': [],
                },
                {
                    'label': 'Political Dynamics',
                    'slug': 'political-dynamics',
                    'pageblocks': [],
                },
                {
                    'label': 'Testing in Applegate',
                    'slug': 'testing-in-applegate',
                    'pageblocks': [],
                },
                {
                    'label': 'Recent Incidences',
                    'slug': 'recent-incidences',
                    'pageblocks': [],
                },
                {
                    'label': 'Your First Decision',
                    'slug': 'your-first-decision',
                    'pageblocks': [
                        {'block_type': 'Text Block'},
                        {
                            'block_type': 'Decision Block',
                            'questions': [{
                                'text': 'Select One',
                                'question_type': 'single choice',
                                'answers': [
                                    {
                                        'value': '1',
                                        'title': 'Choice 1: Full Disclosure',
                                        'description': 'You have chosen to ' +
                                        'address the allegations publicly ' +
                                        'and commence to investigate the ' +
                                        'allegations.',
                                    },
                                    {
                                        'value': '2',
                                        'title': 'Choice 2: Initiate an ' +
                                        'Unofficial Investigation',
                                        'description': 'You decide to ' +
                                        'discreetly conduct your own ' +
                                        'investigation and wait to see'
                                    },
                                    {
                                        'value': '3',
                                        'title': 'Choice 3: Initiate an ' +
                                        'Unofficial Investigation',
                                        'description': 'Manage Quietly ' +
                                        'Behind Closed Doors.'
                                    },
                                ]
                            }],
                        },
                        {
                            'block_type': 'Gate Block',
                            'label': 'First Decision Point',
                        },
                        {'block_type': 'Text Block'},
                    ],
                    'children': [{
                        'label': 'Curve Ball',
                        'slug': 'curve-ball',
                    }]
                },
            ]
        })
        root.add_child_section_from_dict({
            'label': 'Part 2 Choice 1',
            'slug': 'part-2-choice-1',
            'pageblocks': [{
                'css_extra': 'alert alert-warning',
            }],
            'children': [{
                'label': 'Your Second Decision',
                'slug': 'your-second-decision',
                'pageblocks': [],
                'children': [{
                    'label': 'Curve Ball',
                    'slug': 'curve-ball',
                    'pageblocks': [],
                    'children': [{
                        'label': 'Confirm Second Decision',
                        'slug': 'confirm-second-decision',
                        'pageblocks': [],
                        'children': [{
                            'label': 'Discussion of Impact',
                            'slug': 'discussion-of-impact',
                            'pageblocks': [],
                            'children': [{
                                'label': 'Results',
                                'slug': 'results',
                                'pageblocks': [],
                                'children': [{
                                    'label': 'End of Experience',
                                    'slug': 'end-of-experience',
                                    'pageblocks': [],
                                    'children': [{
                                    }]
                                }]
                            }]
                        }]
                    }]
                }]
            }]
        })
        self.root = root
