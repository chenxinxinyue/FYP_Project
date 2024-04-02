from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


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
