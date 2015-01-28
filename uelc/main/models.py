from django.db import models
from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from pagetree.models import Hierarchy, Section
from pageblocks.models import TextBlock



class Cohort(models.Model):
    name = models.CharField(max_length=255, blank=False)
    user = models.ManyToManyField(User, blank=True)

    def __unicode__(self):
        return self.name

    def display_name(self):
        return '%s' % (self.name)

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            name = forms.CharField(widget=forms.widgets.Input(
                attrs={'class': 'add-cohort-name'}))
            user = forms.ModelChoiceField(widget=forms.SelectMultiple(attrs={'class': 'user-select'}),
                                          queryset=User.objects.all().order_by('username'),
                                          empty_label=None)
        return AddForm()


class UserProfile(models.Model):
    PROFILE_CHOICES = (
        (None, '--------'),
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
        return '%s' % (self.user.first_name)

    def is_admin(self):
        return self.profile_type == 'admin'

    def is_assistant(self):
        return self.profile_type == 'assistant'

    def is_group_user(self):
        return self.profile_type == 'group_user'


class CreateUserForm(UserCreationForm):
    user_profile = forms.ChoiceField(
        required=True,
        widget=forms.Select(
            attrs={'class': 'create-user-pofile', 'required': True}),
        choices=UserProfile.PROFILE_CHOICES)
    username = forms.CharField(widget=forms.widgets.Input(attrs={'class': 'add-user-username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'add-user-password1', 'type':'password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'add-user-password2', 'type':'password', 'data-match':"#id_password1"}))
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')



class CreateHierarchyForm(forms.Form):
    name = forms.CharField(
        required=True, 
        widget=forms.widgets.Input(
        attrs={'class': 'add-hierarchy-name', 'required' : True}))

    url = forms.CharField(
        required=True,
        widget=forms.widgets.Input(
            attrs={'class': 'add-hierarchy-url', 'required' : True}),
            label = mark_safe('<strong>Url - the base url for your case.</strong>'))

class Case(models.Model):
    name = models.CharField(max_length=255, blank=False)
    hierarchy = models.ForeignKey(Hierarchy)
    cohort = models.ForeignKey(Cohort, related_name="cohort",
                               default=1, blank=True)

    def __unicode__(self):
        return self.name

    def display_name(self):
        return '%s' % (self.name)

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            name = forms.CharField(widget=forms.widgets.Input(
                attrs={'class': 'add-case-name'}))
            hier = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'hierarchy-select'}),
                                          queryset=Hierarchy.objects.all().order_by('name'),)
            cohort = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'cohort-select'}),
                                          queryset=Cohort.objects.all().order_by('name'),)
        return AddForm()


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
        if len(self.value.split('.')) > 1:
            value = self.value.split('.')[0]
            self.value = value
            self.save()


class CustomSelectWidgetAD(widgets.Select):
    def render(self, name, value, attrs=None):
        return mark_safe(u'''<span>After Decision</span>%s''' %\
            (super(CustomSelectWidgetAD, self).render(name, value, attrs)))


class CustomSelectWidgetAC(widgets.Select):
    def render(self, name, value, attrs=None):
        return mark_safe(u'''<span>After Choice</span>%s''' %\
            (super(CustomSelectWidgetAC, self).render(name, value, attrs)))


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
                label="poop",
                widget=forms.widgets.Textarea(
                    attrs={'cols': 180, 'rows': 40, 'class': 'mceEditor'}))
            after_decision = forms.ChoiceField(
                choices=CHOICES,
                widget= CustomSelectWidgetAD)
            choice = forms.ChoiceField(
                choices=CHOICES,
                widget= CustomSelectWidgetAC)
        return AddForm(auto_id=False)

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
            body = forms.CharField(
                widget=forms.widgets.Textarea(
                    attrs={'cols': 180, 'rows': 40, 'class': 'mceEditor'}),
                initial=self.body)
            after_decision = forms.ChoiceField(choices=CHOICES,
                                             widget= CustomSelectWidgetAD,
                                             initial=self.after_decision)
            choice = forms.ChoiceField(choices=CHOICES,
                                       initial=self.choice,
                                       widget= CustomSelectWidgetAC,)
        return EditForm(auto_id=False)

    def edit(self, vals, files):
        self.body = vals.get('body', '')
        self.after_decision = vals.get('after_decision', '')
        self.choice = vals.get('choice', '')
        self.save()

    def summary_render(self):
        if len(self.body) < 61:
            return self.body.replace("<", "&lt;")
        else:
            return self.body[:61].replace("<", "&lt;") + "..."


class UELCHandler(Section):
    ''' this class is used to handle the logic for
        the decision tree. It translates the add_values
        in the case map into the path for the user along
        the pagetree
    '''

    def get_vals_from_casemap(self, casemap_value):
        vals = [int(i) for i in casemap_value if int(i) > 0]
        return vals

    def get_part_by_section(self, section):
        modules = section.get_root().get_children()
        sec_module = section.get_module()
        part = 0
        for index in range(len(modules)):
            if modules[index] == sec_module:
                part = index
        if part == 0:
            return 1
        else:
            return float(2) + (part * .1)

    def get_partchoice_by_usermap(self, usermap):
        vals = self.get_vals_from_casemap(usermap.value)
        part = 1
        if len(vals) >= 2:
            part = float(2) + (vals[1] * .1)
        return part

    def get_p1c1(self, casemap_value):
        return self.get_vals_from_casemap(casemap_value)[1]

    def can_show(self, request, section, casemap_value):
        cmvl = list(casemap_value)
        tree = section.get_tree()
        section_index = [sec for sec in
                         range(len(tree))
                         if tree[sec] == section][0] + 1
        try:
            content_value = [int(i) for i in
                             reversed(cmvl[0:section_index])
                             if int(i) > 0][0]
        except IndexError:
            content_value = 0

        return content_value

    def can_show_gateblock(self, gate_section, part_usermap):
        can_show = False
        part_section = self.get_part_by_section(gate_section)
        if part_section == 1 or part_section == part_usermap:
            can_show = True
        return can_show

    def p1pre(self, casemap_value):
        p1pre = 0
        vals = self.get_vals_from_casemap(casemap_value)
        if len(vals) > 1:
            p1pre = vals[0]
        return p1pre


class LibraryItem(models.Model):
    name = models.TextField(blank=False)
    doc = models.FileField(upload_to='documents/%Y/%m/%d')
    user = models.ManyToManyField(User, blank=True)
    case = models.ForeignKey(Case)

    template_file = 'main/doc.html'

    def __unicode__(self):
        return self.name

    def display_name(self):
        return '%s' % (self.name)

    def get_users(self):
        return self.case.cohort.user.all()

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            doc = forms.FileField(label="select doc")
            name = forms.CharField(widget=forms.widgets.Textarea(
                attrs={'class': 'library-item-name',
                       'cols': 10,
                       'rows': 2
                       }))
        return AddForm()

    def edit_form(self):
        class EditLibraryForm(forms.Form):
            doc = forms.FileField(initial=self.doc,
                                  label="Replace image")
            name = forms.CharField(
                initial=self.name,
                widget=forms.widgets.Textarea(
                    attrs={'class': 'library-item-name',
                           'cols': 10,
                           'rows': 2
                           }))

        return EditLibraryForm()
