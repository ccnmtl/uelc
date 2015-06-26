from django import forms
from django.db import models
from django.contrib.auth.models import User
from pagetree.models import Section
from pagetree.generic.models import BasePageBlock


class GateBlock(BasePageBlock):
    template_file = "gate_block/gateblock.html"
    display_name = "Gate Block"

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
            gate_user_id=user.id).count() > 0

    def status(self, gate_section, user, hierarchy, uloc):
        """
        Takes self.pageblock().section, a User, Hierarchy, and UserLocation.
        """
        ss_exists = SectionSubmission.objects.filter(
            user=user, section=gate_section).exists()

        for block in gate_section.pageblock_set.all():
            if ss_exists and block.section == gate_section:
                return 'reviewed'

            bk = block.block()
            if bk.display_name == "Decision Block":
                if bk.is_submitted(bk, user):
                    return 'reviewed'

        if self.unlocked(user, gate_section):
            return 'reviewed'

        if gate_section.get_uservisit(user):
            return "reviewing"

        h_url = hierarchy.get_absolute_url()
        uloc_path = h_url + uloc.path
        if uloc_path == gate_section.get_absolute_url():
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
    section = models.ForeignKey(Section, related_name='section_submited')
    user = models.ForeignKey(User, related_name='section_user')
    submitted = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return "section %d submission by %s at %s" % (
            self.section.id,
            unicode(self.user),
            self.submitted)
