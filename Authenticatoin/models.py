from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        """
        Authenticate a user based on email address as the username.
        """
        if email:
            try:
                user = self.get(email=email)
            except self.model.DoesNotExist:
                # Run the default password hasher once to reduce the timing
                # difference between an existing and a nonexistent user (#20760).
                self.model().set_password(password)
            else:
                if user.check_password(password):
                    return user
        return None


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.username
