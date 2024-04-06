# forms.py
import csv

from django import forms
from django.core.validators import MinValueValidator
from django.forms import inlineformset_factory, modelformset_factory
from Authentication.models import CustomUser
from .models import Study, Experience, CV, Preference


class StudyForm(forms.ModelForm):
    DEGREE_CHOICES = [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
    ]

    degree = forms.ChoiceField(choices=DEGREE_CHOICES)
    school = forms.CharField(widget=forms.TextInput(attrs={'id': 'id_school', 'autocomplete': 'off'}))

    class Meta:
        model = Study
        fields = ['degree', 'school']


class ExperienceForm(forms.ModelForm):
    job_detail = forms.CharField(widget=forms.Textarea(attrs={'class': 'full-width-textarea'}))

    class Meta:
        model = Experience
        fields = ['job_title', 'job_detail', 'job_duration']


class CVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = ['cv_file']


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = Preference
        fields = ['preference']


# 定义 Experience 表单集
ExperienceFormSet = inlineformset_factory(
    parent_model=CustomUser,
    model=Experience,
    form=ExperienceForm,
    extra=1,
    can_delete=True,
)
# 定义 Experience 表单集
PreferenceFormSet = inlineformset_factory(
    parent_model=CustomUser,
    model=Preference,
    form=PreferenceForm,
    extra=1,
    can_delete=True,
)
