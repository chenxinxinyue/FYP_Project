from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from Authentication.models import Resume, CustomUser  # 确保正确导入 Resume 模型
from .models import Job # 确保正确导入 Resume 模型
from .utils import extract_keywords  # 假设你有一个工具函数来提取简历中的关键词

CustomUser = get_user_model()


def index(request):
    try:
        user_id = request.session.get('user_id')

        if user_id:
            # Get the user based on their ID
            user = CustomUser.objects.get(id=user_id)

    except CustomUser.DoesNotExist as e:
        print("User does not exist:", e)
    except Exception as e:
        print("An error occurred:", e)

    return render(request, 'index.html', {"user": user})


def upload_view(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']

        # 假设用户已登录，可以直接通过 request.user 获取当前用户
        user = request.user

        keywords = extract_keywords(file)  # 从文件中提取关键词

        # 确保用户已经有一个简历对象
        resume, created = Resume.objects.get_or_create(user=user)
        resume.keywords = keywords  # 假设你的简历模型有一个存储关键词的字段
        resume.save()

        # 上传成功后重定向到首页
        return HttpResponseRedirect(reverse('index'))
    else:
        # 处理非POST请求或未上传文件的情况
        return HttpResponse('Invalid request', status=400)


def favorites_view(request):
    return render(request, 'favorites.html')


def profile_view(request):
    return render(request, 'profile.html')


def jobs_view(request):
    jobs = Job.objects.all()
    return render(request, 'jobs.html', {'jobs': jobs})