from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from pagetree.models import PageBlock
from django.conf import settings
from django.contrib.contenttypes import generic
from django import forms
import os


class GateBlock(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    body = models.TextField(blank=True)
    template_file = "gate_block/gateblock.html"
    display_name = "Gate Block"

    def __unicode__(self):
        return unicode(self.pageblock())

    def redirect_to_self_on_submit(self):
        return True

    def clear_user_submissions(self, user):
        Submission.objects.filter(gateblock_id=self.id, gate_user_id=user.id).delete()

    def pageblock(self):
        return self.pageblocks.all()[0]

    def needs_submit(self):
        return True

    def allow_redo(self):
        return False

    def unlocked(self, user):
        return Submission.objects.filter(gateblock_id=self.id, gate_user_id=user.id).count() > 0

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            body = forms.CharField(
                widget=forms.widgets.Textarea(attrs={'cols': 80}))
        return AddForm()

    @classmethod
    def create(self, request):
        return GateBlock.objects.create(body=request.POST.get('body', ''))

    @classmethod
    def create_from_dict(self, d):
        return GateBlock.objects.create(body=d.get('body', ''))

    def edit_form(self):
        class EditForm(forms.Form):
            body = forms.CharField(widget=forms.widgets.Textarea(),
                                   initial=self.body)
        return EditForm()

    def edit(self, vals, files):
        self.body = vals.get('body', '')
        self.save()

    def as_dict(self):
        return dict(body=self.body)

    def summary_render(self):
        if len(self.body) < 61:
            return self.body
        else:
            return self.body[:61] + "..."

    def submit(self, user, data):
        s = Submission.objects.create(gateblock_id=self.id, gate_user_id=user.id)


class Submission(models.Model):
    gateblock = models.ForeignKey(GateBlock)
    gate_user = models.ForeignKey(User, related_name='gate_user')
    submitted = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return "gate %d submission by %s at %s" % (self.quiz.id,
                                                   unicode(self.user),
                                                   self.submitted)
