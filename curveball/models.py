from datetime import datetime
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from pagetree.models import PageBlock, Section, UserLocation


class Curveball(models.Model):
    title = models.TextField(blank=True)
    explanation = models.TextField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.scenario_type)


class CurveballBlock(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "curveball/curveballblock.html"
    display_name = "Curveball Block"
    description = models.TextField(blank=True)
    exportable = False
    importable = False
    curveball_one = models.ForeignKey(Curveball, null=True, blank=True,
                                      related_name='curveball_one')
    curveball_two = models.ForeignKey(Curveball, null=True, blank=True,
                                      related_name='curveball_two')
    curveball_three = models.ForeignKey(Curveball, null=True, blank=True,
                                        related_name='curveball_three')

    def __unicode__(self):
        return unicode(self.pageblock())

    def redirect_to_self_on_submit(self):
        return True

    def clear_user_submissions(self, user):
        CurveballSubmission.objects.filter(
            curveballblock_id=self.id,
            curveballblock_user_id=user.id).delete()

    def pageblock(self):
        return self.pageblocks.all()[0]

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
        except:
            status = "incomplete"
        return status

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            choice_one_title = forms.CharField(label="Choice One Label")
            choice_one_explanation = forms.CharField(
                label="Choice One Content", widget=forms.widgets.Textarea())
            choice_two_title = forms.CharField(label="Choice Two Label")
            choice_two_explanation = forms.CharField(
                label="Choice Two Content", widget=forms.widgets.Textarea())
            choice_three_title = forms.CharField(label="Choice Three Label")
            choice_three_explanation = forms.CharField(
                label="Choice Three Content", widget=forms.widgets.Textarea())
        return AddForm()

    @classmethod
    def create(cls, request):
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
            choice_one_title = forms.CharField(
                label="Choice One Label", initial=self.curveball_one.title)
            choice_one_explanation = forms.CharField(
                label="Choice One Content",
                initial=self.curveball_one.explanation,
                widget=forms.widgets.Textarea())
            choice_two_title = forms.CharField(
                label="Choice Two Label", initial=self.curveball_two.title)
            choice_two_explanation = forms.CharField(
                label="Choice Two Content",
                initial=self.curveball_two.explanation,
                widget=forms.widgets.Textarea())
            choice_three_title = forms.CharField(
                label="Choice Three Label", initial=self.curveball_three.title)
            choice_three_explanation = forms.CharField(
                label="Choice Three Content",
                initial=self.curveball_three.explanation,
                widget=forms.widgets.Textarea())
        return EditForm()

    def edit(self, vals, files):
        '''Do I need this? The only other
        item that has it is the decision tree'''
        self.curveball_one.title = vals.get('choice_one_title', '')
        self.curveball_one.explanation = vals.get(
            'choice_one_explanation', '')
        self.curveball_two.title = vals.get('choice_two_title', '')
        self.curveball_two.explanation = vals.get(
            'choice_two_explanation', '')
        self.curveball_three.title = vals.get('choice_three_title', '')
        self.curveball_three.explanation = vals.get(
            'choice_three_explanation', '')
        self.save()

    def submit(self, user, data):
        if len(data.keys()) > 0:
            CurveballSubmission.objects.create(curveballblock_id=self.id,
                                               section_id=self.section.id,
                                               curveballblock_user_id=user.id)


class CurveballSubmission(models.Model):
    curveballblock = models.ForeignKey(CurveballBlock)
    curveball_user = models.ForeignKey(User, related_name='curveball_user')
    section = models.ForeignKey(Section)
    submitted = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return "curveball %d submission by %s at %s" % (
            self.curveballblock.id, unicode(self.curveball_user),
            self.submitted)
