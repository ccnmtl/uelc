from django.db import models
from django.contrib.auth.models import User
from pagetree.models import Hierarchy
from decimal import *

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
    cohort = models.ForeignKey(Cohort, related_name="cohort",
                               default=1, blank=True)

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
    value = models.DecimalField(max_digits=6, decimal_places=2, blank=True)

    def get_value(self):
        return self.value

    def set_value(self, quiz, data):
        import pdb
        pdb.set_trace()
        val = self.save_value(quiz, data)
        self.value = val
        self.save()

    def save_value(self, quiz, data):
        # get_depth()
        # root level is 1
        # part level is 2
        # 1st child level is 3 - so this is 
        # really the root or the first level.
        # if value is 0, then this is the first 
        # reveal question of part 1
        # 
        case = Case.objects.get(id = data['case'])
        section = quiz.pageblock().section
        root = section.get_root()
        case_depth = section.get_depth() - 3
        old_val = self.value
        # place is the place value to save
        place_value = self.get_next_place_value(case_depth) 
        val = [v for k,v in data.items() if 'question' in k]
        # important to note that val must be a number (not string)
        # this means admins must place a numerical value in the
        # value field. Might need to require that on the answer
        # field form
        val = float(val[0]) * 1.00
        import pdb
        pdb.set_trace()
        reanswer = self.is_reanswer(case_depth, val)
        if not reanswer:
            print 'setting new val'
            val = val * place_value
            self.value += Decimal(val)
        else: 
            self.resave_choice(case_depth, val)
        self.save()
        return self.value

    def is_reanswer(self, case_depth, val):
        if self.value > 0:
            import pdb
            pdb.set_trace()
            split_val = list(str(int(self.value)))
            if len(split_val) >= case_depth:
                if split_val[case_depth] > 0:
                    return True
        return False


    def resave_choice(self, case_depth, val):
        reval_place = int(self.get_next_place_value(val)) / 10
        string = list(str(int(self.value)))
        old_val_in_place = int(string[case_depth])
        self.value -= old_val_in_place
        self.value += int(val)

    def get_next_place_value(self, val):
        # return the place value to save the submitted 
        # answer value into. 1,10,100,1000,1000, etc. 
        if val > 0:
            val = val * 1.00
            import pdb
            pdb.set_trace()
            string = list(str(val))
            return int(pow(10, (string.index('.')-1)) * 10)
        return 1