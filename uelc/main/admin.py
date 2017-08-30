from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from uelc.main.models import (
    UserProfile, Case, Cohort, CaseMap, CaseQuiz,
    CaseAnswer, TextBlockDT, ImageUploadItem)
from curveball.models import CurveballBlock
from pagetree.models import Hierarchy
from pageblocks.models import TextBlock
from gate_block.models import GateBlock
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.db import models
from ckeditor.widgets import CKEditorWidget


# Define an inline admin descriptor for UserProfile model
# which acts a bit like a singleton
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = True
    verbose_name_plural = 'profile'


# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )


def section_hierarchy(obj):
    return obj.section.hierarchy.name


section_hierarchy.short_description = 'Hierarchy'


class FlatPageCustom(FlatPageAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


class ImageUploadItemAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': forms.widgets.TextInput}
    }


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Hierarchy)
admin.site.register(TextBlock)
admin.site.register(TextBlockDT)
admin.site.register(Case)
admin.site.register(CaseMap)
admin.site.register(CaseQuiz)
admin.site.register(CaseAnswer)
admin.site.register(Cohort)
admin.site.register(ImageUploadItem, ImageUploadItemAdmin)
admin.site.register(GateBlock)
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageCustom)
admin.site.register(CurveballBlock)
