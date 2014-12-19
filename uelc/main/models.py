from django.db import models
from django import forms
from django.contrib.auth.models import User
from pagetree.models import Hierarchy, Section
from pageblocks.models import TextBlock


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
    value = models.TextField(blank=True)

    def get_value(self):
        return self.value

    def set_value(self, quiz, data):
        val = self.save_value(quiz, data)
        self.value = val
        self.save()

    def save_value(self, quiz, data):
        #case = Case.objects.get(id=data['case'])
        section = quiz.pageblock().section
        case_depth = len(section.get_tree())
        count = 0
        section_depth = 0
        for sec in section.get_tree():
            if sec.id == section.id:
                section_depth = count
            count += 1
        # place is the place value to save
        val = [v for k, v in data.items() if 'question' in k]
        val = val[0]
        self.add_value_places(case_depth)
        answerlist = list(self.value)
        answerlist[section_depth] = str(val)
        answers = ''.join(n for n in answerlist)
        self.value = answers

        self.save()
        return self.value

    def add_value_places(self, case_depth):
        self.clean_value()
        init_places = len(self.value) - 1
        if case_depth > init_places:
            x_places = case_depth - init_places
            for place in range(x_places):
                self.value += '0'
            self.save()

    def clean_value(self):
        if self.value.split('.') > 1:
            value = self.value.split('.')[0]
            self.value = value
            self.save()


class TextBlockDT(TextBlock):
    template_file = "pageblocks/textblock.html"
    display_name = "Text BlockDT"
    after_decision = models.CharField(max_length=2, blank=True, default=0)
    choice = models.CharField(max_length=2, blank=True, default=0)

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            CHOICES = ((0, '0'), (1, '1'), (2, '2'),
                       (3, '3'), (4, '4'), (5, '5'))
            choices = models.IntegerField(
                max_length=2,
                choices=CHOICES,
                default=0)
            body = forms.CharField(
                widget=forms.widgets.Textarea(attrs={'cols': 80}))
            after_decision = forms.ChoiceField(choices=CHOICES)
            choice = forms.ChoiceField(choices=CHOICES)
        return AddForm()

    @classmethod
    def create(self, request):
        return TextBlockDT.objects.create(
            body=request.POST.get('body', ''),
            after_decision=request.POST.get('after_decision', ''),
            choice=request.POST.get('choice', ''),
            )

    def edit_form(self):
        class EditForm(forms.Form):
            CHOICES = ((0, '0'), (1, '1'), (2, '2'),
                       (3, '3'), (4, '4'), (5, '5'))
            body = forms.CharField(widget=forms.widgets.Textarea(),
                                   initial=self.body)
            after_decision = forms.ChoiceField(choices=CHOICES,
                                               initial=self.after_decision)
            choice = forms.ChoiceField(choices=CHOICES, initial=self.choice)
        return EditForm()

    def edit(self, vals, files):
        self.body = vals.get('body', '')
        self.after_decision = vals.get('after_decision', '')
        self.choice = vals.get('choice', '')
        self.save()


class UELCHandler(Section):
    ''' this class is used to handle the logic for
        the decision tree. It translates the add_values
        in the case map into the path for the user along
        the pagetree
    '''
    map_obj = dict()

    def create_case_map_list(self, casemap):
        pvl = list(casemap.value)
        pvi = [int(x) for x in pvl]
        return pvi

    def populate_map_obj(self, casemap_list):
        decision_key_list = ['p1pre', 'p1c1', 'p2pre', 'p2c2']
        decision_val_list = []
        for i, v in enumerate(casemap_list):
            if v > 0:
                decision_val_list.append({'tree_index': i, 'value': v})
        for i, v in enumerate(decision_val_list):
            self.map_obj[decision_key_list[i]] = decision_val_list[i]

    def p1pre(self):
        p1pre = False
        try:
            self.map_obj['p1pre']
            p1pre = True
        except:
            pass
        return p1pre

    def p1c1(self):
        p1c1 = False
        try:
            self.map_obj['p1c1']
            p1c1 = True
        except:
            pass
        return p1c1

    def p2pre(self):
        p2pre = False
        try:
            self.map_obj['p2pre']
            p2pre = True
        except:
            pass
        return p2pre

    def p2c2(self):
        p2c2 = False
        try:
            self.map_obj['p2c2']
            p2c2 = True
        except:
            pass
        return p2c2

    def is_p1_zap(self, section):
        if self.p1pre():
            sec_index = self.map_obj['p1pre']['tree_index'] + 1
            if section == section.get_tree()[sec_index]:
                return True
        return False
