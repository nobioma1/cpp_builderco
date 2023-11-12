from django import forms

from .models import Member


class ProjectMemberForm(forms.ModelForm):
    user_email = forms.EmailField(label="Registered user email")
    can_manage_members = forms.BooleanField(required=False)
    can_manage_files = forms.BooleanField(required=False)
    can_manage_project = forms.BooleanField(required=False)

    class Meta:
        model = Member
        fields = ["role"]
