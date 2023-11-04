from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if end_date and start_date >= end_date:
            raise forms.ValidationError("End date must be after the start date.")

        return cleaned_data

    class Meta:
        model = Project
        fields = ["type", "name", "description", "location", "start_date", "end_date", "status"]
