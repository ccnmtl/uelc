import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from pagetree.forms import CloneHierarchyForm
from pagetree.models import Hierarchy
from uelc.main.models import UserProfile, Cohort


class CreateUserForm(UserCreationForm):
    user_profile = forms.ChoiceField(
        required=True,
        widget=forms.Select(
            attrs={'class': 'create-user-profile', 'required': True}),
        choices=UserProfile.PROFILE_CHOICES,
        initial='group_user')
    cohort = forms.ModelChoiceField(
        widget=forms.Select(
            attrs={'class': 'cohort-select'}),
        queryset=Cohort.objects.all().order_by('name'),)
    username = forms.CharField(
        widget=forms.widgets.Input(
            attrs={'class': 'add-user-username'}))
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={'class': 'add-user-password1', 'type': 'password', }))
    password2 = forms.CharField(
        label="Password confirm",
        widget=forms.PasswordInput(
            attrs={'class': 'add-user-password2',
                   'type': 'password',
                   'data-match': "#id_password1"}))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class CreateHierarchyForm(forms.Form):
    name = forms.CharField(
        required=True,
        widget=forms.widgets.Input(
            attrs={'class': 'add-hierarchy-name',
                   'required': True}))


class UELCCloneHierarchyForm(CloneHierarchyForm):
    def clean(self):
        cleaned_data = super(UELCCloneHierarchyForm, self).clean()
        base_url = cleaned_data.get('base_url')

        # Pagetree's clone() function expects a "base_url" parameter
        # to give to the new Hierarchy.  UELC's pagetree is set up to
        # require the base_url to be in the format: /pages/url/
        # I want to handle the case where the user doesn't put the
        # base_url in that format without changing the way pagetree
        # works.
        m = re.match(r'^\/pages\/(\S+)\/$', base_url)
        if m is None:
            # base_url isn't in the recognizable format, so assume it's
            # a slug.
            base_url = '/pages/%s/' % base_url
            if Hierarchy.objects.filter(base_url=base_url).exists():
                raise forms.ValidationError(
                    'There\'s already a hierarchy with ' +
                    'the base_url: {}'.format(base_url))
            cleaned_data['base_url'] = base_url

        return cleaned_data


class EditUserPassForm(forms.Form):
    newPassword1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={'class': 'new-user-password1', 'type': 'password', }))
    newPassword2 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={'class': 'new-user-password2', 'type': 'password', }))


class CaseAnswerForm(forms.Form):
    value = forms.IntegerField(required=True, min_value=1)
    title = forms.CharField(max_length=100, required=True)
    description = forms.CharField(widget=forms.Textarea, required=True)
