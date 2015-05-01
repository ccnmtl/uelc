from datetime import datetime
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from pagetree.models import PageBlock, Section, UserLocation


class CurveballBlock(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "curveball/curveballblock.html"
    display_name = "Curveball Block"

    def __unicode__(self):
        return unicode(self.pageblock())

    def redirect_to_self_on_submit(self):
        return True

    def clear_user_submissions(self, user):
        CurveballSubmission.objects.filter(curveball_id=self.id,
                                           curveball_user_id=user.id).delete()

    def pageblock(self):
        return self.pageblocks.all()[0]

    def needs_submit(self):
        return True

    def allow_redo(self):
        return False

    def unlocked(self, user, section):
        return CurveballSubmission.objects.filter(
            gateblock_id=self.id,
            gate_user_id=user.id).count() > 0

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
            # if for some reason the user is re-doing their entry.
            # if so, the admin would have reset the gates so they
            # can redo their decision
            if not unlocked and page_status == "incomplete":
                status = "in progress"
                return status
        except:
            status = "incomplete"
        return status

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            hidden = forms.HiddenInput()
        return AddForm()

    @classmethod
    def create(self, request):
        return CurveballBlock.objects.create()

    def edit_form(self):
        class EditForm(forms.Form):
            hidden = forms.HiddenInput()
        return EditForm()

    def edit(self, vals, files):
        self.save()

    def submit(self, user, data):
        if len(data.keys()) > 0:
            CurveballSubmission.objects.create(curveballblock_id=self.id,
                                               curveball_user_id=user.id)


class CurveballSubmission(models.Model):
    curveballblock = models.ForeignKey(CurveballBlock)
    curveball_user = models.ForeignKey(User, related_name='curveball_user')
    section = models.ForeignKey(Section)
    submitted = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return "gate %d submission by %s at %s" % (self.curveballblock.id,
                                                   unicode(self.curveball_user),
                                                   self.submitted)
