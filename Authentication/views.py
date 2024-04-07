# Authenticatoin/views.py
import os

import certifi
import random
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from .models import CustomUser

os.environ['SSL_CERT_FILE'] = certifi.where()

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse_lazy


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user using Django's built-in authenticate method
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # The login method takes the HttpRequest and User objects
            # and performs the login (saving the user's ID in the session)
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
        # 检查邮箱是否已经被注册
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email is already registered'})

        if password1 != password2:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        verification_code = str(random.randint(100000, 999999))  # Generate a 6-digit verification code
        send_verification_email_for_register(email, verification_code)
        # print("Generated Verification Code:", verification_code)  # Print the generated verification code

        # Store necessary data in session for verification
        request.session['verification_code'] = verification_code
        request.session['email'] = email
        request.session['password'] = password1

        return redirect(reverse_lazy('Authentication:verify_email'))

    return render(request, 'register.html', {})


def verify_email(request):
    if request.method == 'POST':
        entered_code = str(request.POST.get('verification_code'))  # Convert user input to string
        stored_code = request.session.get('verification_code')
        print(
            entered_code, stored_code
        )
        if entered_code == stored_code:
            create_user_from_session(request)
            return redirect(reverse_lazy('Authentication:login'))
        else:
            return render(request, 'verify_email.html', {'error': 'Invalid verification code'})

    return render(request, 'verify_email.html', {})


def send_verification_email_for_register(email, code):
    send_mail(
        'Verification Code for MainApp Registration',
        f'Your verification code is: {code}',
        'recommendjob@gmail.com',
        [email],
        fail_silently=False,
    )


def create_user_from_session(request):
    email = request.session.get('email')
    password = request.session.get('password')

    try:
        user = CustomUser.objects.create_user(username=email, email=email, password=password)
        print("User created successfully")
        del request.session['verification_code']
        del request.session['email']
        del request.session['password']
    except Exception as e:
        print("An error occurred:", e)


def send_verification_email_for_reset_password(email, message_html):
    send_mail(
        'Password Reset for YourAccount',
        '',
        'no-reply@yourwebsite.com',
        [email],
        fail_silently=False,
        html_message=message_html,
    )


def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                user = CustomUser.objects.get(email=email)
                # Generate a password reset token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                # Construct password reset link
                reset_link = request.build_absolute_uri(
                    f"/login/password_reset_confirm/{uid}/{token}/"
                )
                # Send password reset email
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
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request,
                                 'Your password has been reset successfully. You can now log in with your new password.')
                return redirect(reverse_lazy('Authentication:login'))
            else:
                messages.error(request, 'Passwords do not match. Please try again.')
    else:
        messages.error(request, 'Invalid reset password link.')
        return redirect(reverse_lazy('Authentication:login'))

    return render(request, 'password_reset_confirm.html')
