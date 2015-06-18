import factory
from factory.fuzzy import FuzzyText
from django.contrib.auth.models import User
from curveball.models import Curveball, CurveballBlock, CurveballSubmission


class GroupUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user%03d" % n)
    is_staff = False
    first_name = 'group user'


class CurveballFactory(factory.DjangoModelFactory):
    class Meta:
        model = Curveball

    title = FuzzyText()
    explanation = FuzzyText()


class CurveballBlockFactory(factory.DjangoModelFactory):
    class Meta:
        model = CurveballBlock

    description = FuzzyText()
    curveball_one = factory.SubFactory(CurveballFactory)
    curveball_two = factory.SubFactory(CurveballFactory)
    curveball_three = factory.SubFactory(CurveballFactory)


class CurveballSubmissionFactory(factory.DjangoModelFactory):
    class Meta:
        model = CurveballSubmission

    curveballblock = factory.SubFactory(CurveballBlockFactory)
    group_curveball = factory.SubFactory(GroupUserFactory)
