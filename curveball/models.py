from random import randint

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from pagetree.generic.models import BasePageBlock
from pagetree.models import UserLocation


class Curveball(models.Model):
    title = models.TextField(blank=True)
    explanation = models.TextField(max_length=255, null=True, blank=True)
    ''' create a flag to know whether the curveball has been selected
    by the facilitator to appear for the group or not '''

    def __unicode__(self):
        return unicode(self.title)

    def as_dict(self):
        return {
            'title': self.title,
            'explanation': self.explanation,
        }

    @classmethod
    def create_from_dict(cls, d):
        if type(d) is not dict:
            d = d.as_dict()
        return cls.objects.create(**d)


class CurveballBlock(BasePageBlock):
    template_file = "curveball/curveballblock.html"
    display_name = "Curveball Block"
    description = models.TextField(blank=True)
    curveball_one = models.ForeignKey(Curveball, null=True, blank=True,
                                      related_name='curveball_one')
    curveball_two = models.ForeignKey(Curveball, null=True, blank=True,
                                      related_name='curveball_two')
    curveball_three = models.ForeignKey(Curveball, null=True, blank=True,
                                        related_name='curveball_three')

    def as_dict(self):
        d = super(CurveballBlock, self).as_dict()
        d.update({
            'description': self.description,
            'curveball_one': self.curveball_one.as_dict(),
            'curveball_two': self.curveball_two.as_dict(),
            'curveball_three': self.curveball_three.as_dict(),
        })
        return d

    @classmethod
    def create_from_dict(cls, d):
        d['curveball_one'] = Curveball.create_from_dict(
            d['curveball_one'])
        d['curveball_two'] = Curveball.create_from_dict(
            d['curveball_two'])
        d['curveball_three'] = Curveball.create_from_dict(
            d['curveball_three'])
        return cls.objects.create(**d)

    def _get_section(self):
        return self.pageblock().section

    section = property(_get_section)

    def get_curveballs(self):
        return [self.curveball_one, self.curveball_two, self.curveball_three]

    def get_latest_curveball_submission(self, group_user):
        selected_curveballs = []
        cbs = self.get_curveballs()

        for cb in cbs:
            try:
                cb_sub = cb.curveballsubmission_set.filter(
                    group_curveball=group_user).latest('submitted')
                if cb_sub:
                    selected_curveballs.append(cb_sub)
            except ObjectDoesNotExist:
                pass
        selected_curveballs.sort(key=lambda x: x.submitted)
        if selected_curveballs:
            latest_curveball_submission = selected_curveballs.pop()
            return latest_curveball_submission

        return None

    def redirect_to_self_on_submit(self):
        return False

    def clear_user_submissions(self, user):
        CurveballSubmission.objects.filter(
            curveballblock_id=self.id,
            curveballblock_user_id=user.id).delete()

    def needs_submit(self):
        return True

    def allow_redo(self):
        return False

    def unlocked(self, user, section):
        return CurveballSubmission.objects.filter(
            curveballblock_id=self.id,
            curveballblock_user_id=user.id).count() > 0

    def status(self, user, hierarchy):
        curveball_section = self.pageblock().section
        h_url = hierarchy.get_absolute_url()
        cb_url = curveball_section.get_absolute_url()
        status = 'None'
        unlocked = self.unlocked(user, curveball_section)
        if unlocked:
            status = 'completed'
        try:
            uloc = UserLocation.objects.get_or_create(
                user=user,
                hierarchy=hierarchy)
            uloc_path = h_url + uloc[0].path
            page_status = self.pageblock().section.get_uservisit(user).status
            if uloc_path == cb_url:
                status = "waiting"
                return status
            if not unlocked and page_status == "incomplete":
                status = "in progress"
                return status
        except (UserLocation.MultipleObjectsReturned, ValueError):
            status = "incomplete"
        return status

    @staticmethod
    def add_form():
        class AddForm(forms.Form):
            EDITOR = 'editor-{}'.format(randint(0, 5000))  # nosec
            choice_one_title = forms.CharField(label="Choice One Label")
            choice_one_explanation = forms.CharField(
                label="Choice One Content", widget=CKEditorWidget(
                    attrs={"id": EDITOR + 'add-choice-1'}))
            choice_two_title = forms.CharField(label="Choice Two Label")
            choice_two_explanation = forms.CharField(
                label="Choice Two Content", widget=CKEditorWidget(
                    attrs={"id": EDITOR + 'add-choice-2'}))
            choice_three_title = forms.CharField(label="Choice Three Label")
            choice_three_explanation = forms.CharField(
                label="Choice Three Content", widget=CKEditorWidget(
                    attrs={"id": EDITOR + 'add-choice-3'}))
        return AddForm()

    @staticmethod
    def create(request):
        return CurveballBlock.objects.create(
            curveball_one=Curveball.objects.create(
                title=request.POST.get('choice_one_title', ''),
                explanation=request.POST.get('choice_one_explanation', '')
            ),
            curveball_two=Curveball.objects.create(
                title=request.POST.get('choice_two_title', ''),
                explanation=request.POST.get('choice_two_explanation', '')
            ),
            curveball_three=Curveball.objects.create(
                title=request.POST.get('choice_three_title', ''),
                explanation=request.POST.get('choice_three_explanation', '')
            )
            )

    def edit_form(self):
        class EditForm(forms.Form):
            EDITOR = "editor-" + str(self.id)
            choice_one_title = forms.CharField(
                label="Choice One Label", initial=self.curveball_one.title)
            choice_one_explanation = forms.CharField(
                label="Choice One Content",
                initial=self.curveball_one.explanation,
                widget=CKEditorWidget(attrs={"id": EDITOR + 'choice-one'}))
            choice_two_title = forms.CharField(
                label="Choice Two Label", initial=self.curveball_two.title)
            choice_two_explanation = forms.CharField(
                label="Choice Two Content",
                initial=self.curveball_two.explanation,
                widget=CKEditorWidget(attrs={"id": EDITOR + 'choice-two'}))
            choice_three_title = forms.CharField(
                label="Choice Three Label", initial=self.curveball_three.title)
            choice_three_explanation = forms.CharField(
                label="Choice Three Content",
                initial=self.curveball_three.explanation,
                widget=CKEditorWidget(attrs={"id": EDITOR + 'choice-three'}))
        return EditForm()

    ''' a form so the facilitator can choose which curball to throw to
    the group user '''
    def curveball_select_form(self):
        class CurveballSelectForm(forms.Form):
            CURVEBALL_CHOICES = (
                (self.curveball_one.id, self.curveball_one),
                (self.curveball_two.id, self.curveball_two),
                (self.curveball_three.id, self.curveball_three),
            )
            curveball = forms.ChoiceField(
                required=True,
                label='Assign Curveball',
                widget=forms.Select(
                    attrs={'class': 'curveball-select', 'required': True}),
                choices=CURVEBALL_CHOICES,
                initial='1')

        return CurveballSelectForm()

    def edit(self, vals, files):
        self.curveball_one.title = vals.get('choice_one_title', '')
        self.curveball_one.explanation = vals.get(
            'choice_one_explanation', '')
        self.curveball_one.save()
        self.curveball_two.title = vals.get('choice_two_title', '')
        self.curveball_two.explanation = vals.get(
            'choice_two_explanation', '')
        self.curveball_two.save()
        self.curveball_three.title = vals.get('choice_three_title', '')
        self.curveball_three.explanation = vals.get(
            'choice_three_explanation', '')
        self.curveball_three.save()
        self.save()

    def create_submission(self, group_user, curveball):
        CurveballSubmission.objects.create(
            curveball=curveball,
            curveballblock=self,
            group_curveball=group_user)


class CurveballSubmission(models.Model):
    curveball = models.ForeignKey(Curveball, null=True, blank=True)
    curveballblock = models.ForeignKey(CurveballBlock)
    '''associate the group with the curveball so we know
    what group this curveball belongs to'''
    group_curveball = models.ForeignKey(User, related_name='curveball_user')
    '''group user has been shown curveball and has read it'''
    group_confirmation = models.BooleanField(default=False)
    submitted = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "curveball %d submission by %s at %s for choice %s" % (
            self.curveballblock.id, unicode(self.group_curveball),
            self.submitted, unicode(self.curveball))
