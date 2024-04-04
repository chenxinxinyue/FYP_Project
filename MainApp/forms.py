from django import forms
from .models import Study, Experience, CV, Preference


class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['degree', 'school']


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['job_title', 'job_description', 'job_duration']


class CVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = ['cv_file']


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = Preference
        fields = ['preference']
