from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


def home(request):
    return render(request, 'home.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
import random
import string


def generate_verification_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        verification_code = request.POST['verification_code']

        # 检查邮箱是否已经被注册
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        # 检查验证码是否匹配
        if 'verification_code' not in request.session or request.session['verification_code'] != verification_code:
            messages.error(request, "Invalid verification code.")
            return redirect('register')

        # 创建新用户并保存到数据库
        user = User.objects.create_user(email=email, password=password)
        user.save()

        # 注册成功后的重定向逻辑
        return redirect('login')  # 将 'login' 替换为你的登录页面 URL 名称
    else:
        # 生成验证码并存储到 session 中
        verification_code = generate_verification_code()
        request.session['verification_code'] = verification_code

        return render(request, 'register.html', {'verification_code': verification_code})


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # 登录成功后的重定向逻辑
            return redirect('home')  # 将 'home' 替换为你的首页 URL 名称
        else:
            # 登录失败时的处理逻辑
            error_message = "Invalid username or password. Please try again."
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')
