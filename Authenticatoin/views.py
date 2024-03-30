# Authenticatoin/views.py
import os

import html2text
from django.core.mail import send_mail
from .models import CustomUser
import certifi
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import mark_safe

os.environ['SSL_CERT_FILE'] = certifi.where()


# from django.contrib.auth import authenticate, login


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # 使用 CustomUserManager 中的 authenticate 方法进行用户认证
        user = CustomUser.objects.authenticate(request, email=email, password=password)
        print(user)

        if user is not None:
            # 如果认证成功，使用 Django 的 login 函数进行用户登录
            # login(request, user)
            # 重定向到 MainApp 应用的首页
            print("登陆成功")
            return redirect('MainApp:index')
        else:
            # 如果认证失败，返回登录页面并显示错误消息
            error_message = "Invalid username or password."
            return render(request, 'login.html', {'error_message': error_message})

    # 如果是 GET 请求，渲染空的登录表单
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

        return redirect('verify_email')

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
            return redirect('login')  # Assuming 'index' is your home view
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
    # print("Entering create_user_from_session function")
    email = request.session.get('email')
    password = request.session.get('password')
    # print("Email:", email)
    # print("Password:", password)

    try:
        user = CustomUser.objects.create_user(username=email, email=email, password=password)
        print("User created successfully")
        # login(request, user)
        # print("User logged in")
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
                return redirect('login')
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
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match. Please try again.')
    else:
        messages.error(request, 'Invalid reset password link.')
        return redirect('login')

    return render(request, 'password_reset_confirm.html')
