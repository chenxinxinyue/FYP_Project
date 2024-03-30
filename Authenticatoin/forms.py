from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email


class PasswordResetForm(forms.Form):
    email = forms.CharField(label='Email', validators=[validate_email])

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No user with this email address.")
        return email
