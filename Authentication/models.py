from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import models


class CustomUserManager(BaseUserManager):
    # Method to create a user
    def create_user(self, username, email, password=None, **extra_fields):
        # Check if email is provided, raise ValueError if not
        if not email:
            raise ValueError('The Email field must be set')

        # Normalize email address
        email = self.normalize_email(email)

        # Validate the password
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                # If password does not meet validation criteria, raise ValueError with error messages
                raise ValueError('\n'.join(e.messages))

        # Create a new user instance
        user = self.model(username=username, email=email, **extra_fields)

        # Set the user's password
        user.set_password(password)

        # Save the user using the database
        user.save(using=self._db)
        return user


# Define a custom user model class that extends AbstractUser
class CustomUser(AbstractUser):
    # Define additional fields for the user model
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=15, blank=True, null=True)

    # Specify the custom user manager for this model
    objects = CustomUserManager()

    # Method to return a string representation of the user object
    def __str__(self):
        return self.username
