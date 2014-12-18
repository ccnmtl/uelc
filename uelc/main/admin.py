from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from uelc.main.models import UserProfile,\
    Case, Cohort, CaseMap, Decision, Choice
from pagetree.models import Hierarchy


# Define an inline admin descriptor for UserProfile model
# which acts a bit like a singleton
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    readonly_fields = ('cohorts',)
    can_delete = True
    verbose_name_plural = 'profile'


# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )


def section_hierarchy(obj):
    return obj.section.hierarchy.name
section_hierarchy.short_description = 'Hierarchy'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Hierarchy)
admin.site.register(Case)
admin.site.register(CaseMap)
admin.site.register(Cohort)
admin.site.register(Decision)
admin.site.register(Choice)
