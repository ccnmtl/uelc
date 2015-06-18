import factory
from django.contrib.auth.models import User

from pagetree.models import Hierarchy
from quizblock.models import Quiz, Question

from uelc.main.models import (
    Cohort, UserProfile, Case, CaseMap,
    CaseAnswer,
    TextBlockDT, UELCHandler,
    LibraryItem, CaseQuiz
)
from curveball.models import CurveballBlock
from curveball.tests.factories import CurveballFactory


class CohortFactory(factory.DjangoModelFactory):
    class Meta:
        model = Cohort

    name = factory.Sequence(lambda n: "cohort %03d" % n)


class AdminUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "admin%03d" % n)
    is_superuser = True
    first_name = 'admin user'
    password = factory.PostGenerationMethodCall('set_password', 'test')


class FacilitatorUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user%03d" % n)
    is_staff = False
    first_name = 'facilitator user'


class GroupUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user%03d" % n)
    is_staff = False
    first_name = 'group user'


class AdminUpFactory(factory.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(AdminUserFactory)
    cohort = factory.SubFactory(CohortFactory)
    profile_type = 'admin'


class FacilitatorUpFactory(factory.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(FacilitatorUserFactory)
    cohort = factory.SubFactory(CohortFactory)
    profile_type = 'assistant'


class GroupUpFactory(factory.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(GroupUserFactory)
    cohort = factory.SubFactory(CohortFactory)
    profile_type = 'group_user'


class HierarchyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Hierarchy

    base_url = "/pages/case-one/"
    name = "case-one"


class CaseFactory(factory.DjangoModelFactory):
    class Meta:
        model = Case

    name = factory.Sequence(lambda n: "case %03d" % n)
    hierarchy = factory.SubFactory(HierarchyFactory)


class CaseMapFactory(factory.DjangoModelFactory):
    class Meta:
        model = CaseMap

    case = factory.SubFactory(CaseFactory)
    user = factory.SubFactory(GroupUserFactory)


class QuizFactory(factory.DjangoModelFactory):
    class Meta:
        model = Quiz


class CaseQuizFactory(factory.DjangoModelFactory):
    class Meta:
        model = CaseQuiz


class QuestionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Question


class TextBlockDTFactory(factory.DjangoModelFactory):
    class Meta:
        model = TextBlockDT


class UELCHandlerFactory(factory.DjangoModelFactory):
    class Meta:
        model = UELCHandler

    depth = 1
    hierarchy = factory.SubFactory(HierarchyFactory)


class LibraryItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = LibraryItem

    name = factory.Sequence(lambda n: "item %03d" % n)
    case = factory.SubFactory(CaseFactory)


class UELCModuleFactory(object):
    """
    A factory for creating a production-like tree of Sections/Pageblocks
    for testing UELC.
    """
    def __init__(self):
        hierarchy = HierarchyFactory(name='case-test',
                                     base_url='/pages/case-test/')
        # hierarchy: case-test at /pages/case-test/
        case = CaseFactory(name='case-test', hierarchy=hierarchy)
        hierarchy = case.hierarchy

        root = hierarchy.get_root()
        root.add_child_section_from_dict({
            'label': 'Part 1',
            'slug': 'part-1',
            'pageblocks': [{
                # The 'Text Block' in UELC is custom.
                'block_type': 'Text Block',
                'label': 'Test Edit Facilitator Scratchpad',
                'body': 'These elements use Bootstrap for styling.',
            }],
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
                            'allow_redo': False,
                            'show_submit_state': False,
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
                        'pageblocks': [
                            {
                                'block_type': 'Gate Block',
                                'label': 'Curveball',
                            },
                            {
                                'block_type': 'Curveball Block',
                                'description': 'Curveball description',
                                'curveball_one': CurveballFactory(),
                                'curveball_two': CurveballFactory(),
                                'curveball_three': CurveballFactory(),
                            },
                        ],
                        'children': [{
                            'label': 'Confirm First Decision',
                            'slug': 'confirm-first-decision',
                            'pageblocks': [{
                                'block_type': 'Gate Block',
                                'label': 'Confirm First Decision',
                            }],
                            'children': [{
                                'label': 'Discussion of Impact',
                                'slug': 'discussion-of-impact',
                                'pageblocks': [{
                                    'block_type': 'Gate Block',
                                    'label': 'Discussion of Impact',
                                }],
                                'children': [{
                                    'label': 'Results',
                                    'slug': 'results',
                                    'pageblocks': [{
                                        'block_type': 'Gate Block',
                                        'label': 'Results of First Decision',
                                    }],
                                }]
                            }]
                        }]

                    }]
                },
            ]
        })

        # Assert that the Quiz imported correctly.
        question = Question.objects.filter(text='Select One').last()
        answers = question.answer_set.all()
        assert answers.count() == 3
        answer = answers.get(value='1')
        ca = CaseAnswer.objects.get(answer=answer)
        assert ca.title == 'Choice 1: Full Disclosure'

        # Assert that the Quiz imported correctly.
        assert CurveballBlock.objects.count() == 1
        cb = CurveballBlock.objects.first()
        assert cb.description == 'Curveball description'

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
                    'pageblocks': [{
                        'block_type': 'Curveball Block',
                        'label': 'Curveball Block',
                        'description': 'Curveball description',
                        'curveball_one': CurveballFactory(),
                        'curveball_two': CurveballFactory(),
                        'curveball_three': CurveballFactory(),
                    }],
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
