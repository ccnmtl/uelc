from django import forms
from django.contrib.auth.models import User
from django.db import models
from pagetree.generic.models import BasePageBlock
from pagetree.models import Section
from quizblock.models import Submission


class GateBlock(BasePageBlock):
    template_file = "gate_block/gateblock.html"
    display_name = "Gate Block"

    @classmethod
    def create_from_dict(cls, d):
        return cls.objects.create(**d)

    def redirect_to_self_on_submit(self):
        return True

    def clear_user_submissions(self, user):
        GateSubmission.objects.filter(gateblock_id=self.id,
                                      gate_user_id=user.id).delete()

    def pageblock(self):
        return self.pageblocks.first()

    def needs_submit(self):
        return True

    def allow_redo(self):
        return False

    def unlocked(self, user, section):
        return GateSubmission.objects.filter(
            gateblock_id=self.id,
            gate_user_id=user.id).exists()

    def status(self, user, uloc, unlocked, pageblocks):
        """
        Takes self.pageblock().section, a User, Hierarchy, UserLocation,
        and optionally, a pageblock set.
        """

        gate_section = self.pageblock().section
        if gate_section.section_submitted.filter(user=user).exists():
            return 'reviewed'

        quizzes = pageblocks.filter(
            content_type__app_label='main',
            content_type__model='casequiz').values_list('object_id', flat=True)
        if Submission.objects.filter(user=user, quiz__id__in=quizzes).exists():
            return 'reviewed'

        if unlocked:
            return 'reviewed'

        if gate_section.get_uservisit(user):
            return "reviewing"

        if uloc.path == gate_section.get_path():
            return "reviewing"

        return "to be reviewed"

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            hidden = forms.HiddenInput()
        return AddForm()

    @classmethod
    def create(self, request):
        return GateBlock.objects.create()

    def edit_form(self):
        class EditForm(forms.Form):
            hidden = forms.HiddenInput()
        return EditForm()

    def edit(self, vals, files):
        self.save()

    def submit(self, user, data):
        if len(data.keys()) > 0:
            GateSubmission.objects.create(gateblock_id=self.id,
                                          gate_user_id=user.id)


class GateSubmission(models.Model):
    gateblock = models.ForeignKey(GateBlock)
    gate_user = models.ForeignKey(User, related_name='gate_user')
    section = models.ForeignKey(Section)
    submitted = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "gate %d submission by %s at %s" % (self.gateblock.id,
                                                   unicode(self.gate_user),
                                                   self.submitted)


class SectionSubmission(models.Model):
    section = models.ForeignKey(Section, related_name='section_submitted')
    user = models.ForeignKey(User, related_name='section_user')
    submitted = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return "section %d submission by %s at %s" % (
            self.section.id,
            unicode(self.user),
            self.submitted)
