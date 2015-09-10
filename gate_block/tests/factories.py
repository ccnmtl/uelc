import factory
from django.contrib.auth.models import User
from pagetree.models import Section
from gate_block.models import GateBlock, GateSubmission, SectionSubmission


class GroupUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user%03d" % n)
    is_staff = False
    first_name = 'group user'


class GateBlockFactory(factory.DjangoModelFactory):
    class Meta:
        model = GateBlock


class SectionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Section


class GateSubmissionFactory(factory.DjangoModelFactory):
    class Meta:
        model = GateSubmission

    gateblock = factory.SubFactory(GateBlockFactory)
    gate_user = factory.SubFactory(GroupUserFactory)
    section = factory.SubFactory(SectionFactory)


class SectionSubmissionFactory(factory.DjangoModelFactory):
    class Meta:
        model = SectionSubmission

    section = factory.SubFactory(SectionFactory)
    user = factory.SubFactory(GroupUserFactory)
