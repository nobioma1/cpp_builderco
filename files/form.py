from django import forms

from .models import ProjectFile


class ProjectFileForm(forms.ModelForm):
    file = forms.FileField(label="Select a file to upload")
    name = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={"placeholder": "Name is optional if uploading another version of existing file"}),
                           required=False)

    class Meta:
        model = ProjectFile
        fields = ["file", "name"]
