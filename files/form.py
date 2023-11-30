from django import forms

from .models import ProjectFile


class ProjectFileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)  # Extract the project

        super().__init__(*args, **kwargs)

        self.fields['category'].required = False

        if project is not None:
            self.fields['existing_file'].queryset = ProjectFile.objects.filter(project=project)

    is_new_version = forms.BooleanField(label="Upload new version of existing file", required=False)
    existing_file = forms.ModelChoiceField(queryset=ProjectFile.objects.none(), empty_label="No Project file selected",
                                           label="Select Existing File", required=False)
    file = forms.FileField(label="Select a file to upload")
    name = forms.CharField(label="File name", max_length=100, widget=forms.TextInput(), required=False)

    def clean_existing_file(self):
        file = self.cleaned_data["existing_file"]

        if not file:
            return None

        return str(file.id)

    def clean(self):
        cleaned_data = super().clean()

        is_new_version = cleaned_data.get('is_new_version')
        existing_file = cleaned_data.get('existing_file')
        file = cleaned_data.get('file')
        name = cleaned_data.get('name')
        category = cleaned_data.get('category')

        if not file:
            raise forms.ValidationError("File is required")

        if is_new_version:
            if not existing_file:
                raise forms.ValidationError("Select existing file to upload version")
        else:
            if not name:
                raise forms.ValidationError("Name is required")
            if not category:
                raise forms.ValidationError("Category is required")

        return cleaned_data

    class Meta:
        model = ProjectFile
        fields = ["is_new_version", "existing_file", "file", "name", "category"]
