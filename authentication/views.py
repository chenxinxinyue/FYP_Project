# authentication/views.py

from django.shortcuts import render


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


# authentication/views.py

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect


# ... (保留已有的 login_view 函数)

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('index')  # 假设你有一个名为 'index' 的视图作为首页
    return render(request, 'register.html', {})


def password_reset_view(request):
    # 这里可以使用Django内置的密码重置视图和表单，或自定义逻辑
    # 省略具体实现细节
    return render(request, 'password_reset.html', {})
