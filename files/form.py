from django import forms

from .models import ProjectFile


class ProjectFileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existing_file_choices = [(file.id, file.name) for file in ProjectFile.objects.all()]
        self.fields['existing_file'].choices = existing_file_choices

    is_new_version = forms.BooleanField(label="Upload new version of existing file", required=False)
    existing_file = forms.ChoiceField(choices=[], label="Select Existing File*", required=False)
    file = forms.FileField(label="Select a file to upload")
    name = forms.CharField(max_length=20, widget=forms.TextInput(), required=True)

    class Meta:
        model = ProjectFile
        fields = ["is_new_version", "existing_file", "file", "name", "category"]
