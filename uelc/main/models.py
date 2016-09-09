from random import randint

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.auth.models import User, Permission
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.forms import widgets
from django.utils.safestring import mark_safe
from pageblocks.models import TextBlock
from pagetree.models import Hierarchy, Section
from pagetree.reports import ReportableInterface
from quizblock.models import Quiz, Question, Submission, Response, Answer

from gate_block.models import GateSubmission


class Cohort(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        unique=True)

    def __unicode__(self):
        return self.name

    def display_name(self):
        return '%s' % (self.name)

    def _get_case(self):
        """Returns all the cases for this Cohort as a queryset."""
        return Case.objects.filter(cohort=self.id)

    def casename(self):
        casenames = [case.name.encode(
            encoding='UTF-8',
            errors='strict') for case in self.case]
        nms = ', '.join(casenames)
        return nms

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
    def add_form(cls):
        class AddForm(forms.Form):
            name = forms.CharField(widget=forms.widgets.Input(
                attrs={'class': 'add-cohort-name'}))
        return AddForm()

    def edit_form(self):
        class EditForm(forms.Form):
            name = forms.CharField(
                initial=self.name,
                widget=forms.widgets.Input(
                    attrs={'class': 'edit-cohort-name'}))
            users = forms.ModelChoiceField(
                initial=[user.id for user in self.users],
                widget=forms.SelectMultiple(
                    attrs={'class': 'user-select'}),
                queryset=User.objects.all().order_by('username'),
                empty_label=None)
        return EditForm()


class UserProfile(models.Model):
    PROFILE_CHOICES = (
        ('admin', 'Administrator'),
        ('assistant', 'Assistant'),
        ('group_user', 'Group User'),
    )
    user = models.OneToOneField(User, related_name="profile")
    profile_type = models.CharField(max_length=12, choices=PROFILE_CHOICES)
    cohort = models.ForeignKey(
        Cohort,
        related_name="user_profile_cohort",
        blank=True,
        null=True)

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

    def set_image_upload_permissions(self, user):
        permission_set = Permission.objects.filter(
            content_type__model="imageuploaditem")
        for perm in permission_set:
            if user.is_staff:
                user.user_permissions.add(perm.pk)
            else:
                user.user_permissions.remove(perm.pk)

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


class Case(models.Model):
    name = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=True, null=True)
    hierarchy = models.ForeignKey(Hierarchy)
    cohort = models.ManyToManyField(
        Cohort,
        related_name="case_cohort",
        blank=True)
    status = models.CharField(
        max_length=1,
        choices=(
            ('a', 'archived'),
            ('d', 'in development'),
            ('p', 'published')),
        default='d')

    def __unicode__(self):
        return self.name

    def display_name(self):
        return '%s' % (self.name)

    def _get_cohorts(self):
        cohorts = Cohort.objects.filter(case_cohort=self.id)
        return cohorts

    def cohortnames(self):
        if self.cohort.all():
            cohortnames = [cohort.name.encode(
                encoding='UTF-8',
                errors='strict') for cohort in self.cohorts]
            nms = ', '.join(cohortnames)
            return nms

    cohorts = property(_get_cohorts)

    @classmethod
    def add_form(cls):
        class AddForm(forms.Form):
            name = forms.CharField(widget=forms.widgets.Input(
                attrs={'class': 'add-case-name'}))
            description = forms.CharField(widget=forms.widgets.Textarea(
                attrs={'class': 'add-case-description'}))
            hierarchy = forms.ModelChoiceField(
                widget=forms.Select(
                    attrs={'class': 'hierarchy-select'}),
                queryset=Hierarchy.objects.all().order_by('name'),)
            cohort = forms.ModelChoiceField(
                widget=forms.Select(
                    attrs={'class': 'cohort-select'}),
                queryset=Cohort.objects.all().order_by('name'),)
        return AddForm()

    def edit_form(self):
        class EditForm(forms.Form):
            name = forms.CharField(
                widget=forms.widgets.Input(
                    attrs={'class': 'add-case-name'}),
                initial=self.name
            )

            description = forms.CharField(
                widget=forms.widgets.Textarea(
                    attrs={'class': 'add-case-description'}),
                initial=self.description
            )

            hierarchy = forms.ModelChoiceField(
                initial=self.hierarchy,
                widget=forms.Select(
                    attrs={'class': 'hierarchy-select'}),
                queryset=Hierarchy.objects.all().order_by('name'),)

            cohort = forms.ModelChoiceField(
                initial=[cohort.id for cohort in self.cohort.all()],
                widget=forms.SelectMultiple(
                    attrs={'class': 'cohort-select'}),
                queryset=Cohort.objects.all().order_by('name'),)

        return EditForm()


class CustomSelectWidgetAC(widgets.Select):
    def render(self, name, value, attrs=None):
        return mark_safe(
            u'''<span class="after-choice">After Choice - \
                <span class="small">the content that will \
                show for the decision made. This is \
                cohort-wide.</span></span>%s''' %
            (super(CustomSelectWidgetAC, self).render(name, value, attrs)))


class CaseMap(models.Model):
    case = models.ForeignKey(Case)
    user = models.ForeignKey(User)
    # each tens place represents a decision, where the decimal
    # place represents temporary decisons
    value = models.TextField(blank=True)

    def get_value(self):
        return self.value

    def set_value(self, quiz, data):
        val = self.save_value(quiz.pageblock().section, data)
        self.value = val
        self.save()

    def save_value(self, section, data):
        case_depth = section.get_tree().count()
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


class TextBlockDT(TextBlock):
    template_file = "pageblocks/textblock.html"
    display_name = "Text Block"
    choice = models.CharField(max_length=2, blank=True, default=0)

    @classmethod
    def add_form(cls):
        class AddForm(forms.Form):
            EDITOR = 'editor-{}'.format(randint(0, 5000))
            CHOICES = ((0, '0'), (1, '1'), (2, '2'),
                       (3, '3'), (4, '4'), (5, '5'))
            choices = models.IntegerField(
                max_length=2,
                choices=CHOICES,
                default=0)
            body = forms.CharField(
                widget=CKEditorWidget(attrs={"id": EDITOR}))
            choice = forms.ChoiceField(
                choices=CHOICES,
                widget=CustomSelectWidgetAC)
        return AddForm(auto_id=False)

    @classmethod
    def create(cls, request):
        return TextBlockDT.objects.create(
            body=request.POST.get('body', ''),
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
            choice = forms.ChoiceField(
                choices=CHOICES,
                initial=self.choice,
                widget=CustomSelectWidgetAC)
        return EditForm(auto_id=False)

    def edit(self, vals, files):
        self.body = vals.get('body', '')
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
        key = 'uelc.{}.get_part_by_section'.format(section.pk)
        v = cache.get(key)
        if v is not None:
            return v

        modules = section.get_root().get_children()
        sec_module = section.get_module()
        part = 0
        for idx, module in enumerate(modules):
            if module == sec_module:
                part = idx

        if part == 0:
            v = 1
        else:
            v = float(2) + (part * .1)

        cache.set(key, v)
        return v

    def get_partchoice_by_usermap(self, usermap):
        vals = self.get_vals_from_casemap(usermap.value)
        part = 1
        if len(vals) >= 2:
            part = float(2) + (vals[1] * .1)
        if len(vals) >= 4:
            part = part + float((vals[3] * .01))
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

    def can_show_gateblock(self, gate_section, part_usermap,
                           part_section=None):
        if part_section is None:
            part_section = self.get_part_by_section(gate_section)

        can_show = False
        if part_section == 1 or part_section == round(part_usermap, 1):
            can_show = True
        return can_show

    def p1pre(self, casemap_value):
        p1pre = 0
        vals = self.get_vals_from_casemap(casemap_value)
        if len(vals) > 1:
            p1pre = vals[0]
        return p1pre

    def is_curveball(self, current_section, pageblocks=None):
        block = None
        if pageblocks is None and current_section is not None:
            pageblocks = current_section.pageblock_set.all()
        if pageblocks:
            for pb in pageblocks:
                block = pb.block()
                if (hasattr(block, 'display_name') and
                        block.display_name == "Curveball Block"):
                    return (True, block)
        return (False, block)

    def is_decision_block(self, current_section, user, pageblocks=None):
        if pageblocks is None:
            pageblocks = current_section.pageblock_set.all()
        for pb in pageblocks:
            block = pb.block()
            if (hasattr(block, 'display_name') and
                    block.display_name == "Decision Block"):
                ss = block.submission_set.filter(user=user).last()
                ca = None
                if ss:
                    response = ss.response_set.filter(
                        submission_id=ss.id).last()
                    ca = CaseAnswer.objects.get(answer=response.answer())
                return (True, block, ca)
        return (False, None, None)

    def is_next_curveball(self, section):
        key = 'uelc.{}.is_next_curveball'.format(section.pk)
        v = cache.get(key)
        if v is not None:
            return v

        nxt = section.get_next()
        is_cb = self.is_curveball(nxt)
        if is_cb[0]:
            cache.set(key, is_cb)
            return is_cb
        else:
            cache.set(key, False)
            return False


class LibraryItem(models.Model):
    name = models.TextField(blank=False)
    doc = models.FileField(upload_to='documents/%Y/%m/%d', max_length=255)
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
    def add_form(cls):
        class AddForm(forms.Form):
            doc = forms.FileField(label="select doc", max_length=255)
            name = forms.CharField(widget=forms.widgets.Textarea(
                attrs={'class': 'library-item-name',
                       'cols': 10,
                       'rows': 2
                       }))
        return AddForm()

    def edit_form(self):
        class EditLibraryForm(forms.Form):
            doc = forms.FileField(initial=self.doc,
                                  label="Replace image",
                                  max_length=255)
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
    doc = models.FileField(upload_to='documents/%Y/%m/%d', max_length=255)

    def __unicode__(self):
        return self.name

    def display_name(self):
        return '%s' % (self.name)


class CaseQuiz(Quiz):
    display_name = "Decision Block"
    template_file = "quizblock/quizblock.html"

    @classmethod
    def create(cls, request):
        return cls.objects.create(
            description=request.POST.get('description', ''),
            rhetorical=request.POST.get('rhetorical', ''),
            allow_redo=request.POST.get('allow_redo', ''),
            show_submit_state=request.POST.get('show_submit_state', False))

    @classmethod
    def create_from_dict(cls, d):
        q = cls.objects.create(
            description=d.get('description', ''),
            rhetorical=d.get('rhetorical', False),
            allow_redo=d.get('allow_redo', True),
            show_submit_state=d.get('show_submit_state', True)
        )
        q.import_from_dict(d)
        return q

    def import_from_dict(self, d):
        self.description = d.get('description', '')
        self.rhetorical = d.get('rhetorical', False)
        self.allow_redo = d.get('allow_redo', True)
        self.show_submit_state = d.get('show_submit_state', True)
        self.save()
        self.submission_set.all().delete()
        self.question_set.all().delete()
        for q in d.get('questions', []):
            question = Question.objects.create(
                quiz=self,
                text=q.get('text', ''),
                question_type=q.get('question_type', None),
                explanation=q.get('explanation', ''),
                intro_text=q.get('intro_text', ''),
                css_extra=q.get('css_extra', ''))
            for a in q.get('answers', []):
                x = Answer.objects.create(
                    question=question,
                    value=a.get('value', None),
                    label=a.get('label', ''),
                    correct=a.get('correct', False),
                    css_extra=a.get('css_extra', ''))
                CaseAnswer.objects.create(
                    answer=x,
                    title=a.get('title', ''),
                    description=a.get('description', ''),
                )
                if 'explanation' in a:
                    x.explanation = a.get('explanation', '')
                    x.save()

    def as_dict(self):
        d = dict(description=self.description,
                 rhetorical=self.rhetorical,
                 allow_redo=self.allow_redo,
                 show_submit_state=self.show_submit_state)

        questions = self.question_set.all()
        d['questions'] = [q.as_dict() for q in questions]
        answers = Answer.objects.filter(question__in=questions)
        for q in d['questions']:
            for answer in answers:
                a = [x for x in q['answers'] if x['value'] == answer.value]
                if len(a) > 0:
                    ca = CaseAnswer.objects.get(answer=answer)
                    a = a[0]
                    a['title'] = ca.title
                    a['description'] = ca.description
                else:
                    # This means the answer won't be exported correctly.
                    pass
        return d

    @classmethod
    def add_form(cls):
        class AddForm(forms.Form):
            description = forms.CharField(widget=forms.widgets.Textarea())
        return AddForm()

    def edit_form(self):
        class EditForm(forms.Form):
            description = forms.CharField(
                widget=forms.widgets.Textarea(),
                initial=self.description)
            alt_text = ("<a href=\"" + reverse("edit-quiz", args=[self.id]) +
                        "\">manage decision/choices</a>")
        return EditForm()

    def is_q_answered(self, data):
        for k in data.keys():
            if k.startswith('question'):
                return True

    def submit(self, user, data):
        """ Do not allow blank submissions """
        if not self.is_q_answered(data):
            return

        s = Submission.objects.create(quiz=self, user=user)
        self.create_casemap_for_user(user, data, s)

    def create_casemap_for_user(self, user, data, s):
        # create a CaseMap for the user
        # get Case the user is currently on
        for k in data.keys():
            if k.startswith('case'):
                self.make_casemap(user, data, s, k)
            if k.startswith('question'):
                self.make_question(user, data, s, k)

    def make_casemap(self, user, data, s, k):
        case_id = data[k]
        try:
            casemap, created = CaseMap.objects.get_or_create(
                user=user, case_id=case_id)
        except CaseMap.MultipleObjectsReturned:
            casemap = CaseMap.objects.filter(
                user=user, case_id=case_id).first()

        casemap.set_value(self, data)

    def make_question(self, user, data, s, k):
        qid = int(k[len('question'):])
        question = Question.objects.get(id=qid)
        # it might make more sense to just accept a QueryDict
        # instead of a dict so we can use getlist()
        dlist = []
        if isinstance(data[k], list):
            dlist = data[k]
        else:
            dlist = [data[k]]

        for v in dlist:
            Response.objects.create(submission=s, question=question, value=v)

    def is_submitted(self, quiz, user):
        return Submission.objects.filter(
            quiz=self,
            user=user).count() > 0

    def unlocked(self, user, section):
        # meaning that the user can proceed *past* this one,
        # not that they can access this one. careful.
        unlocked = False
        submissions = GateSubmission.objects.filter(gate_user_id=user.id)
        if submissions.count() > 0:
            for sub in submissions:
                section = sub.gateblock.pageblock().section
                upv = section.get_uservisit(user)
                blocks = section.pageblock_set.all()
                for block in blocks:
                    obj = block.content_object
                    if obj.display_name == "Gate Block":
                        unlocked = obj.unlocked(user, section)
            is_quiz_submitted = self.is_submitted(self, user)
            if upv:
                upv.status = 'complete'
                upv.save()
                if not (unlocked and is_quiz_submitted):
                    unlocked = False
                else:
                    unlocked = True
        return unlocked


class CaseAnswer(models.Model):
    def default_question(self):
        return self.answer.question_id

    answer = models.ForeignKey(Answer)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)

    def display_answer(self):
        return self.answer

    def display_title(self):
        return self.title

    def display_description(self):
        return self.description

    def edit_form(self, request=None):
        class CaseAnswerForm(forms.Form):
            value = forms.IntegerField(initial=self.answer.value)
            title = forms.CharField(initial=self.title)
            description = forms.CharField(
                widget=forms.Textarea,
                initial=self.description)
        return CaseAnswerForm()

    def as_dict(self):
        return {
            'title': self.title,
            'description': self.description,
        }

ReportableInterface.register(CaseQuiz)
