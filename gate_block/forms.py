from django import forms
from django.forms import widgets


class AddGateBlockForm(forms.Form):
    label = forms.CharField()
    body = forms.CharField(widget=widgets.Textarea(attrs={'cols': 80}))

