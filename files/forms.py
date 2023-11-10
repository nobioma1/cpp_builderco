from django import forms


class UploadForm(forms.Form):
    file = forms.FileField(label="Select a file to upload")
    file_name = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={"placeholder": "Name is optional if uploading another version of existing file"}),
                                required=False)
