from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

from Authentication.models import CustomUser


class Job(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    detail_url = models.URLField()

    def __str__(self):
        return self.name


class DetailedJob(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    med_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    formatted_work_type = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    remote_allowed = models.BooleanField(default=False)
    job_posting_url = models.URLField()
    application_type = models.CharField(max_length=100, null=True, blank=True)
    skills_desc = models.TextField(null=True, blank=True)
    work_type = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.title


class Resume(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resume')
    summary = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Resume"


class Study(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100)
    school = models.CharField(max_length=100)


class Experience(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100)
    job_description = models.TextField()
    job_duration = models.CharField(max_length=100)


class CV(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    cv_file = models.FileField(upload_to='cvs/')


class Preference(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    preference = models.CharField(max_length=100)