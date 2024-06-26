# forms.py

from django import forms
from django.forms import inlineformset_factory

from Authentication.models import CustomUser
from .models import Study, Experience, CV, Preference


class StudyForm(forms.ModelForm):
    DEGREE_CHOICES = [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
    ]

    degree = forms.ChoiceField(choices=DEGREE_CHOICES, widget=forms.Select(attrs={'class': 'larger-select'}))
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

    def clean_cv_file(self):
        cv_file = self.cleaned_data.get('cv_file')
        if cv_file:
            file_extension = cv_file.name.split('.')[-1].lower()
            if file_extension not in ['pdf', 'docx', 'doc']:
                raise forms.ValidationError("Only PDF, DOCX, and DOC formats are allowed.")
        return cv_file


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = Preference
        fields = ('preference',)
        widgets = {
            'preference': forms.TextInput(attrs={
                'id': 'id_preference',
                'class': 'preference-autocomplete'  # Add this class
            }),
        }


# Define Experience formset
ExperienceFormSet = inlineformset_factory(
    parent_model=CustomUser,
    model=Experience,
    form=ExperienceForm,
    extra=1,
    can_delete=True,
)
# Define Preference formset
PreferenceFormSet = inlineformset_factory(
    parent_model=CustomUser,
    model=Preference,
    form=PreferenceForm,
    extra=1,
    can_delete=True,
)
