# Authentication/views.py

import os
import random
from datetime import timezone

import certifi
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .models import CustomUser
from .utils import send_verification_email_for_register, send_verification_email_for_reset_password

os.environ['SSL_CERT_FILE'] = certifi.where()


def login_view(request):
    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            print("{} Login Successful".format(user.email))
            return redirect(reverse_lazy('MainApp:index'))
        else:
            error_message = "Invalid email or password."
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html', {})


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm_password')

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email is already registered'})

        if password1 != password2:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        try:
            validate_password(password1)
        except ValidationError as e:
            return render(request, 'register.html', {'error': '\n'.join(e.messages)})

        verification_code = str(random.randint(100000, 999999))
        send_verification_email_for_register(email, verification_code)

        request.session['verification_code'] = verification_code
        request.session['email'] = email
        request.session['password'] = password1

        return redirect(reverse_lazy('Authentication:verify_email'))

    return render(request, 'register.html')
from django.core.exceptions import ValidationError

def custom_password_validator(password):
    # 检查密码长度是否符合要求
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

    # 检查密码是否包含特殊字符
    special_characters = "!@#$%^&*()_-+="
    if not any(char in special_characters for char in password):
        raise ValidationError("Password must contain at least one special character.")

    # 检查密码是否包含数字
    if not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one digit.")

    # 检查密码是否包含大写字母
    if not any(char.isupper() for char in password):
        raise ValidationError("Password must contain at least one uppercase letter.")

    # 检查密码是否包含小写字母
    if not any(char.islower() for char in password):
        raise ValidationError("Password must contain at least one lowercase letter.")


from django.contrib import messages


def verify_email(request):

    if request.method == 'POST':
        entered_code = str(request.POST.get('verification_code'))
        stored_code = request.session.get('verification_code')
        # CAPTCHA comparison
        if stored_code and entered_code == stored_code:
            user_created = create_user_from_session(request)
            if user_created:
                messages.success(request, "User created successfully. Please login.")
                return redirect(reverse_lazy('Authentication:login'))
            else:
                messages.error(request, "An error occurred during user creation.")
        else:
            messages.error(request, 'Invalid verification code')

    return render(request, 'verify_email.html')


def create_user_from_session(request):
    email = request.session.get('email')
    password = request.session.get('password')

    if not email or not password:
        return False

    try:
        CustomUser.objects.create_user(username=email, email=email, password=password)
        clear_registration_session(request)
        return True
    except Exception as e:
        print("An error occurred while creating the user:", e)
        return False


def clear_registration_session(request):
    for key in ['verification_code', 'email', 'password', 'verification_timestamp']:
        try:
            del request.session[key]
        except KeyError:
            pass


def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                user = CustomUser.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = request.build_absolute_uri(
                    f"/login/password_reset_confirm/{uid}/{token}/"
                )
                message_html = render_to_string('password_reset_email.html', {
                    'user': user,
                    'reset_link': reset_link,
                })
                send_verification_email_for_reset_password(email, message_html)
                messages.success(request,
                                 'An email with password reset instructions has been sent to your email address.')
                return redirect(reverse_lazy('Authentication:login'))
            except CustomUser.DoesNotExist:
                messages.error(request, 'No user found with this email address.')
        else:
            messages.error(request, 'Please provide an email address.')
    return render(request, 'password_reset.html')


def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = str(urlsafe_base64_decode(uidb64), 'utf-8')
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        messages.error(request, 'The password reset link is invalid, possibly because it has already been used.')
        return redirect(reverse_lazy('Authentication:login'), status=404)

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match. Please try again.')
                return render(request, 'password_reset_confirm.html')

            try:
                validate_password(new_password, user)
            except ValidationError as e:
                messages.error(request, '\n'.join(e.messages))
                return render(request, 'password_reset_confirm.html')

            user.set_password(new_password)
            user.save()
            messages.success(request,
                             'Your password has been reset successfully. You can now log in with your new password.')
            return redirect(reverse_lazy('Authentication:login'))
    else:
        messages.error(request, 'Invalid reset password link.')
        return redirect(reverse_lazy('Authentication:login'))

    return render(request, 'password_reset_confirm.html')
