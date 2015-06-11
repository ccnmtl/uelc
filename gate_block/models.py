from datetime import datetime
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from pagetree.models import PageBlock, Section, UserLocation


class GateBlock(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "gate_block/gateblock.html"
    display_name = "Gate Block"

    def __unicode__(self):
        return unicode(self.pageblock())

    def redirect_to_self_on_submit(self):
        return True

    def clear_user_submissions(self, user):
        GateSubmission.objects.filter(gateblock_id=self.id,
                                      gate_user_id=user.id).delete()

    def pageblock(self):
        return self.pageblocks.all()[0]

    def needs_submit(self):
        return True

    def allow_redo(self):
        return False

    def unlocked(self, user, section):
        return GateSubmission.objects.filter(
            gateblock_id=self.id,
            gate_user_id=user.id).count() > 0

    def status(self, user, hierarchy):
        gate_section = self.pageblock().section
        h_url = hierarchy.get_absolute_url()
        gs_url = gate_section.get_absolute_url()
        status = 'None'
        unlocked = self.unlocked(user, gate_section)
        if unlocked:

            status = 'reviewed'
            return status
        
        uloc = UserLocation.objects.get_or_create(
            user=user,
            hierarchy=hierarchy)
        uloc_path = h_url + uloc[0].path
        
        uv = self.pageblock().section.get_uservisit(user)

        if uv:
            status = "reviewing"
            return status

        if uloc_path == gs_url:
            status = "reviewing"
            return status
        # if for some reason the user is re-doing their entry.
        # if so, the admin would have reset the gates so they
        # can redo their decision
        #
        #if not unlocked and page_status == "to be reviewed":
        #    status = "in progress"
        #    return status
    
        status = "to be reviewed"
        return status

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
    submitted = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return "gate %d submission by %s at %s" % (self.gateblock.id,
                                                   unicode(self.gate_user),
                                                   self.submitted)
