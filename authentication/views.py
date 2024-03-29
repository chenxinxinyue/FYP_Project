# authentication/views.py
import os
import random  # Make sure to import random module
from CJob.models import CustomUser  # 导入你的自定义用户模型
import certifi
from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

os.environ['SSL_CERT_FILE'] = certifi.where()


def login_view(request):
    # If the form has been submitted...
    if request.method == 'POST':
        # Process the data in form.cleaned_data
        # (this is where you would authenticate the user)
        pass
    # If a GET (or any other method) we'll create a blank form
    else:
        pass

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
        # print("断点1")
        if entered_code == stored_code:
            # print("断点2")
            create_user_from_session(request)
            # print("断点3")
            return redirect('index')  # Assuming 'index' is your home view
        else:
            return render(request, 'verify_email.html', {'error': 'Invalid verification code'})

    return render(request, 'verify_email.html', {})

# def index(request):


def send_verification_email(email, code):
    send_mail(
        'Verification Code for CJob Registration',
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
        user = User.objects.create_user(username=email, email=email, password=password)
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
