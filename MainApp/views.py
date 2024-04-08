import pandas as pd
from django.core.management import call_command
from django.http import HttpResponseRedirect
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
from django.contrib.auth.decorators import login_required


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


from django.http import JsonResponse
from .models import School


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


def favorites_view(request):
    return render(request, 'favorites.html')


def jobs_view(request):
    jobs = Job.objects.all()
    return render(request, 'jobs.html', {'jobs': jobs})


def load_file(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'inline; filename="{file_name}"'
            return response
    else:
        return HttpResponse("File not found", status=404)


def find_jobs(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            location = form.cleaned_data['address']
            call_command('job_scraper', location)

            messages.success(request, 'Address updated successfully.')
            # print(form.cleaned_data)
            return redirect('MainApp:show-jobs')

    else:
        form = CustomUserForm(instance=user)

    context = {
        'form': form,
    }
    return render(request, 'show_jobs.html', context)


def show_jobs(request):
    try:
        jobs = pd.read_csv("static/file/jobs.csv")
        selected_columns = ['title', 'location', 'job_type', 'is_remote']
        jobs = jobs[selected_columns]

        context = {
            'jobs': jobs.to_dict('records'),
            'columns': jobs.columns.tolist()
        }
    except FileNotFoundError:
        context = {'error': 'Job listings not found. Please initiate a search first.'}

    return render(request, 'show_jobs.html', context)
