from django.db import models
from django.contrib.auth.models import User
from quizblock.models import Submission
from pagetree.models import Hierarchy, Section


class Cohort(models.Model):
    name = models.CharField(max_length=255, blank=False)
    user = models.ManyToManyField(User, blank=True)

    def __unicode__(self):
        return self.name

    def display_name(self):
        return '%s - %s' % (self.name)


class UserProfile(models.Model):
    PROFILE_CHOICES = (
        ('admin', 'Administrator'),
        ('assistant', 'Assistant'),
        ('group_user', 'Group User'),
    )
    user = models.OneToOneField(User, related_name="profile")
    profile_type = models.CharField(max_length=12, choices=PROFILE_CHOICES)

    def _get_cohorts(self):
        cohorts = Cohort.objects.filter(user=self.user.id)
        cohort_names = [cohort.name.encode(encoding='UTF-8',
                        errors='strict') for cohort in cohorts]
        cts = ', '.join(cohort_names)
        return cts

    cohorts = property(_get_cohorts)

    def __unicode__(self):
        return self.user.username

    class Meta:
        ordering = ["user"]

    def display_name(self):
        return '%s - %s' % (self.user.first_name)

    def is_admin(self):
        return self.profile_type == 'AD'

    def is_assistant(self):
        return self.profile_type == 'AS'

    def is_group_user(self):
        return self.profile_type == 'GU'


class Case(models.Model):
    name = models.CharField(max_length=255, blank=False)
    hierarchy = models.ForeignKey(Hierarchy)
    cohort = models.ForeignKey(Cohort,
                               related_name="cohort",
                               default=1,
                               blank=True)

    def __unicode__(self):
        return self.name

    def display_name(self):
        return '%s - %s' % (self.name)

    @classmethod
    def create(self, cohort, hierarchy):
        case = self(name=self.name,
                    hierarchy=self.hierarchy,
                    cohort=self.cohort)
        return case


class CaseMap(models.Model):
    case = models.ForeignKey(Case)
    user = models.ForeignKey(User)
    # each tens place represents a decision, where the decimal
    # place represents temporary decisons
    value = models.DecimalField(max_digits=6, decimal_places=2)

'''
class GateSubmission(models.Model):
    submission = models.ForeignKey(Submission)
    user = models.ForeignKey(User)
    section = models.ForeignKey(Section)
'''