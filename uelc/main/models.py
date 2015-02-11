from django.db import models
from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from pagetree.models import Hierarchy, Section, ReportableInterface
from ckeditor.widgets import CKEditorWidget
from pageblocks.models import TextBlock
from quizblock.models import Quiz, Question, Submission, Response
from gate_block.models import GateSubmission
from django.core.exceptions import ObjectDoesNotExist


class Cohort(models.Model):
    name = models.CharField(max_length=255, blank=False)

    def __unicode__(self):
        return self.name

    def display_name(self):
        return '%s' % (self.name)

    def _get_case(self):
        case = Case.objects.get(cohort=self.id)
        if not case:
            return None
        return case

    def _get_users(self):
        upros = UserProfile.objects.filter(
            cohort=self.id).order_by('user__username')
        users = [up.user for up in upros if up.cohort.id == self.id]
        return users

    def usernames(self):
        unames = [user.username.encode(
            encoding='UTF-8',
            errors='strict') for user in self.users]
        nms = ', '.join(unames)
        return nms

    case = property(_get_case)
    users = property(_get_users)

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            name = forms.CharField(widget=forms.widgets.Input(
                attrs={'class': 'add-cohort-name'}))
            user = forms.ModelChoiceField(
                widget=forms.SelectMultiple(
                    attrs={'class': 'user-select'}),
                queryset=User.objects.all().order_by('username'),
                empty_label=None)
        return AddForm()

    def edit_form(self):
        class EditForm(forms.Form):
            name = forms.CharField(
                initial=self.name,
                widget=forms.widgets.Input(
                    attrs={'class': 'edit-cohort-name'}))
            user = forms.ModelChoiceField(
                initial=[user.id for user in self.users],
                widget=forms.SelectMultiple(
                    attrs={'class': 'user-select'}),
                queryset=User.objects.all().order_by('username'),
                empty_label=None)
            if self.case:
                initial = self.case.id
            else:
                initial = ''
            case = forms.ModelChoiceField(
                initial=[self.case.id if self.case else 0],
                widget=forms.Select(
                    attrs={'class': 'case-select'}),
                queryset=Case.objects.all().order_by('name'),)
        return EditForm()


class UserProfile(models.Model):
    PROFILE_CHOICES = (
        (None, '--------'),
        ('admin', 'Administrator'),
        ('assistant', 'Assistant'),
        ('group_user', 'Group User'),
    )
    user = models.OneToOneField(User, related_name="profile")
    profile_type = models.CharField(max_length=12, choices=PROFILE_CHOICES)
    cohort = models.ForeignKey(
        Cohort,
        related_name="user_profile_cohort",
        default=1)

    def edit_form(self):
        class EditForm(forms.Form):
            username = forms.CharField(
                widget=forms.widgets.Input(
                    attrs={'class': 'edit-user-username'}),
                initial=self.user.username)
            profile_type = forms.ChoiceField(
                initial=self.profile_type,
                required=True,
                widget=forms.Select(
                    attrs={'class': 'create-user-profile', 'required': True}),
                choices=UserProfile.PROFILE_CHOICES)
            cohort = forms.ModelChoiceField(
                initial=self.cohort,
                widget=forms.Select(
                    attrs={'class': 'cohort-select'}),
                queryset=Cohort.objects.all().order_by('name'),)
        return EditForm()

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
            attrs={'class': 'create-user-profile', 'required': True}),
        choices=UserProfile.PROFILE_CHOICES)
    cohort = forms.ModelChoiceField(
        widget=forms.Select(
            attrs={'class': 'cohort-select'}),
        queryset=Cohort.objects.all().order_by('name'),)
    username = forms.CharField(
        widget=forms.widgets.Input(
            attrs={'class': 'add-user-username'}))
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={'class': 'add-user-password1', 'type': 'password', }))
    password2 = forms.CharField(
        label="Password confirm",
        widget=forms.PasswordInput(
            attrs={'class': 'add-user-password2',
                   'type': 'password',
                   'data-match': "#id_password1"}))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class CreateHierarchyForm(forms.Form):
    name = forms.CharField(
        required=True,
        widget=forms.widgets.Input(
            attrs={'class': 'add-hierarchy-name',
                   'required': True}))

    url = forms.CharField(
        required=True,
        widget=forms.widgets.Input(
            attrs={'class': 'add-hierarchy-url', 'required': True}),
        label=mark_safe('<strong>Url - the base url for your case.</strong>'))


class Case(models.Model):
    name = models.CharField(max_length=255, blank=False)
    hierarchy = models.ForeignKey(Hierarchy)
    cohort = models.ManyToManyField(
        Cohort,
        related_name="case_cohort",
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
            hierarchy = forms.ModelChoiceField(
                widget=forms.Select(
                    attrs={'class': 'hierarchy-select'}),
                queryset=Hierarchy.objects.all().order_by('name'),)
            cohort = forms.ModelChoiceField(
                widget=forms.Select(
                    attrs={'class': 'cohort-select'}),
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
        return mark_safe(
            u'''<span>After Decision</span>%s''' %
            (super(CustomSelectWidgetAD, self).render(name, value, attrs)))


class CustomSelectWidgetAC(widgets.Select):
    def render(self, name, value, attrs=None):
        return mark_safe(
            u'''<span>After Choice</span>%s''' %
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
                widget=CKEditorWidget(attrs={"id": "editor"}))
            after_decision = forms.ChoiceField(
                choices=CHOICES,
                widget=CustomSelectWidgetAD)
            choice = forms.ChoiceField(
                choices=CHOICES,
                widget=CustomSelectWidgetAC)
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
            EDITOR = "editor-" + str(self.id)
            CHOICES = ((0, '0'), (1, '1'), (2, '2'),
                       (3, '3'), (4, '4'), (5, '5'))
            body = forms.CharField(
                widget=CKEditorWidget(attrs={"id": EDITOR}),
                initial=self.body)
            after_decision = forms.ChoiceField(
                choices=CHOICES,
                widget=CustomSelectWidgetAD,
                initial=self.after_decision)
            choice = forms.ChoiceField(
                choices=CHOICES,
                initial=self.choice,
                widget=CustomSelectWidgetAC)
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

    def get_users(self, cohort):
        upros = UserProfile.objects.filter(cohort=cohort)
        users = [profile.user for profile in upros]
        return users

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


class ImageUploadItem(models.Model):
    name = models.TextField(blank=False)
    doc = models.FileField(upload_to='documents/%Y/%m/%d')

    def __unicode__(self):
        return self.name

    def display_name(self):
        return '%s' % (self.name)


class CaseQuiz(Quiz):
    display_name = "Case Quiz"
    template_file = "quizblock/quizblock.html"

    @classmethod
    def get_pageblock(self):
        return True

    @classmethod
    def create(self, request):
        return CaseQuiz.objects.create(
            description=request.POST.get('description', ''),
            rhetorical=request.POST.get('rhetorical', ''),
            allow_redo=request.POST.get('allow_redo', ''),
            show_submit_state=request.POST.get('show_submit_state', False))

    @classmethod
    def create_from_dict(self, d):
        q = CaseQuiz.objects.create(
            description=d.get('description', ''),
            rhetorical=d.get('rhetorical', False),
            allow_redo=d.get('allow_redo', True),
            show_submit_state=d.get('show_submit_state', True)
        )
        q.import_from_dict(d)
        return q

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            description = forms.CharField(widget=forms.widgets.Textarea())
            rhetorical = forms.BooleanField()
            allow_redo = forms.BooleanField()
            show_submit_state = forms.BooleanField(initial=True)
        return AddForm()

    def submit(self, user, data):
        """ a big open question here is whether we should
        be validating submitted answers here, on submission,
        or let them submit whatever garbage they want and only
        worry about it when we show the admins the results """
        s = Submission.objects.create(quiz=self, user=user)
        # create a CaseMap for the user
        # get Case the user is currently on
        quiz = self
        for k in data.keys():
            if k.startswith('case'):
                case_id = data[k]
                try:
                    casemap = CaseMap.objects.get(
                        user=user,
                        case_id=case_id)

                except ObjectDoesNotExist:
                    casemap = CaseMap.objects.create(
                        user=user,
                        case_id=case_id,
                        value=str(0))

                casemap.set_value(quiz, data)

            if k.startswith('question'):
                qid = int(k[len('question'):])
                question = Question.objects.get(id=qid)
                # it might make more sense to just accept a QueryDict
                # instead of a dict so we can use getlist()
                if isinstance(data[k], list):
                    for v in data[k]:
                        Response.objects.create(
                            submission=s,
                            question=question,
                            value=v)
                else:
                    Response.objects.create(
                        submission=s,
                        question=question,
                        value=data[k])

    def is_submitted(self, quiz, user):
        return Submission.objects.filter(
            quiz=self,
            user=user).count() > 0

    def unlocked(self, user, section):
        # meaning that the user can proceed *past* this one,
        # not that they can access this one. careful.
        unlocked = False
        submissions = GateSubmission.objects.filter(gate_user_id=user.id)
        if len(submissions) > 0:
            for sub in submissions:
                section_id = sub.gateblock.pageblock().section_id
                section = Section.objects.get(id=section_id)
                upv = section.get_uservisit(user)
                blocks = section.pageblock_set.all()
                for block in blocks:
                    obj = block.content_object
                    if obj.display_name == "Gate Block":
                        unlocked = obj.unlocked(user, section)
            is_quiz_submitted = self.is_submitted(self, user)
            if not (unlocked and is_quiz_submitted):
                unlocked = False
                upv.status = 'complete'
                upv.save()
            else:
                upv.status = 'complete'
                upv.save()
                unlocked = True
        return unlocked

ReportableInterface.register(CaseQuiz)
