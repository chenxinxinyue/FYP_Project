import pandas as pd
from django.core.management import call_command
from django.http import HttpResponseRedirect, FileResponse
from django.urls import reverse
from Authentication.forms import CustomUserForm
from .models import Job
from .utils import extract_keywords
from django.shortcuts import render, redirect
from .forms import StudyForm, ExperienceForm, CVForm, PreferenceForm, ExperienceFormSet, PreferenceFormSet
from .models import CustomUser, Study, Experience, CV, Preference, Resume
from django.http import HttpResponse
from django.conf import settings
import os
from django.contrib import messages
from django.http import JsonResponse
from .models import School


def index(request):
    user = None  # 在此处初始化 user 变量

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


def profile_view(request):
    user = request.user
    study_instance, _ = Study.objects.get_or_create(user=user)
    experience_instances = Experience.objects.filter(user=user)
    cv_instance, _ = CV.objects.get_or_create(user=user)
    preference_instances = Preference.objects.filter(user=user)

    if request.method == 'POST':
        study_form = StudyForm(request.POST, instance=study_instance)
        experience_formset = ExperienceFormSet(request.POST, instance=user, queryset=experience_instances)
        cv_form = CVForm(request.POST, request.FILES, instance=cv_instance)
        preference_formset = PreferenceFormSet(request.POST, instance=user, queryset=preference_instances)

        if not experience_formset.is_valid():
            print("Experience Formset Errors:", experience_formset.errors)
        if study_form.is_valid() and experience_formset.is_valid() and cv_form.is_valid() and preference_formset.is_valid():
            study_form.save()
            experience_formset.save()
            cv_form.save()
            preference_formset.save()
            messages.success(request,
                             'Update your profile successfully.')
            return redirect("MainApp:profile")
    else:
        study_form = StudyForm(instance=study_instance)
        experience_formset = ExperienceFormSet(instance=user, queryset=experience_instances)
        cv_form = CVForm(instance=cv_instance)
        preference_formset = PreferenceFormSet(instance=user, queryset=preference_instances)
        print(experience_formset)

    context = {
        'study_form': study_form,
        'experience_form': experience_formset,
        'cv_form': cv_form,
        'preference_form': preference_formset,
    }
    return render(request, 'profile.html', context)


def get_schools(request):
    term = request.GET.get('term', '')
    schools = School.objects.filter(name__icontains=term)[:10]
    schools_data = [{'label': school.name, 'value': school.name} for school in schools]
    return JsonResponse(schools_data, safe=False)


def get_jobs(request):
    term = request.GET.get('term', '')
    jobs = Job.objects.filter(name__icontains=term)[:10]
    jobs_data = [{'label': job.name, 'value': job.name} for job in jobs]
    return JsonResponse(jobs_data, safe=False)


def upload_view(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']

        user = request.user

        keywords = extract_keywords(file)

        # 确保用户已经有一个简历对象
        resume, created = Resume.objects.get_or_create(user=user)
        resume.keywords = keywords  # 假设你的简历模型有一个存储关键词的字段
        resume.save()

        # 上传成功后重定向到首页
        return HttpResponseRedirect(reverse('index'))
    else:
        # 处理非POST请求或未上传文件的情况
        return HttpResponse('Invalid request', status=400)


from django.shortcuts import redirect, render
from .models import FavoriteJob


def favorites_view(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        is_favorited = request.POST.get('is_favorited')

        user = request.user
        if is_favorited == 'true':
            # 取消收藏
            FavoriteJob.objects.filter(user=user, id=id).delete()
            # 重定向到收藏页面
            return redirect('MainApp:favorites')
        else:
            favorite_jobs = FavoriteJob.objects.filter(user=user)
            return render(request, 'favorites.html', {'favorite_jobs': favorite_jobs})
    else:
        favorite_jobs = FavoriteJob.objects.filter(user=request.user)
        return render(request, 'favorites.html', {'favorite_jobs': favorite_jobs})


def jobs_view(request):
    jobs = Job.objects.all()
    return render(request, 'jobs.html', {'jobs': jobs})


# views.py

def load_file(request, file_name):
    # 如果路径中有尾部斜杠，移除它
    file_name = file_name.rstrip('/')
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:  # 使用 with 语句确保文件正确关闭
            return FileResponse(file, as_attachment=True)
    else:
        return HttpResponse("File not found", status=404)


def find_jobs(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            location = form.cleaned_data['address']
            job_preferences = Preference.objects.filter(user=user).values_list('preference', flat=True)
            job_preferences_list = list(job_preferences)
            # 传递用户 ID 作为额外参数
            call_command('job_scraper', location, job_preferences=job_preferences_list, user_id=user.id)

            messages.success(request, 'Address and job preferences updated successfully.')
            return redirect('MainApp:show-jobs')
    else:
        form = CustomUserForm(instance=user)
    context = {'form': form}
    return render(request, 'show_jobs.html', context)


def show_jobs(request):
    user = request.user
    user_id = user.id
    print(f"user_id:{user_id}")
    # Correct the way to format the string to include the user_id in the file path
    file_path = f"static/file/jobs_{user_id}.csv"

    try:
        jobs = pd.read_csv(file_path)
        selected_columns = ['job_url', 'title', 'location', 'is_remote']
        jobs = jobs[selected_columns]
        context = {
            'jobs': jobs.to_dict('records'),  # Convert the DataFrame into a list of dictionaries for the template
            'columns': selected_columns  # Use the list directly since we're specifying the columns
        }
    except FileNotFoundError:
        context = {'error': 'Job listings not found. Please initiate a search first.'}

    return render(request, 'show_jobs.html', context)


from django.http import JsonResponse
from .models import FavoriteJob
from django.http import JsonResponse
from .models import FavoriteJob


def favorite_job(request):
    if request.method == 'POST':
        job_url = request.POST.get('job_url')
        title = request.POST.get('title')
        location = request.POST.get('location')
        is_remote = request.POST.get('is_remote')
        is_favorited = request.POST.get('is_favorited')

        # 替换为默认值
        if location is None:
            location = "Unknown"

        # 处理 is_remote 的值
        if is_remote is not None:
            is_remote = is_remote.lower() == 'true'
        else:
            is_remote = False

        user = request.user
        if is_favorited == 'true':
            FavoriteJob.objects.filter(user=user, job_url=job_url).delete()
        else:
            favorite_job = FavoriteJob(user=user, job_url=job_url, title=title, location=location,
                                       is_remote=is_remote)
            favorite_job.save()

        return JsonResponse({'message': 'Operation successful'})
    else:
        return JsonResponse({'error': 'Unauthorized or invalid request!'}, status=401)
