# Authenticatoin/views.py
import os
import random  # Make sure to import random module
from .models import CustomUser
import certifi
from django.core.mail import send_mail
from django.shortcuts import render, redirect

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

        if password1 != password2:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        verification_code = str(random.randint(100000, 999999))  # Generate a 6-digit verification code
        send_verification_email(email, verification_code)
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


# def index(request):


def send_verification_email(email, code):
    send_mail(
        'Verification Code for MainApp Registration',
        f'Your verification code is: {code}',
        'recommendjob@gmail.com',
        [email],
        fail_silently=False,
    )


def create_user_from_session(request):
    print("Entering create_user_from_session function")
    email = request.session.get('email')
    password = request.session.get('password')
    print("Email:", email)
    print("Password:", password)

    try:
        user = CustomUser.objects.create_user(username=email, email=email, password=password)
        print("User created successfully")
        login(request, user)
        print("User logged in")
        del request.session['verification_code']
        del request.session['email']
        del request.session['password']
    except Exception as e:
        print("An error occurred:", e)


def password_reset_view(request):
    # 这里可以使用Django内置的密码重置视图和表单，或自定义逻辑
    # 省略具体实现细节
    return render(request, 'password_reset.html', {})
