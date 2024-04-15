import csv
import os

import pandas as pd
from django.contrib import messages
from django.http import HttpResponseRedirect, FileResponse, HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from jobspy import scrape_jobs
from pandas.errors import EmptyDataError

from pyresparser import ResumeParser

from Authentication.forms import CustomUserForm
from .forms import StudyForm, CVForm, ExperienceFormSet, PreferenceFormSet
from .models import Job, School, CustomUser, Study, Experience, CV, Preference, Resume, FavoriteJob
from .utils import extract_keywords


def index(request):
    user = None  # Initialize the user variable

    try:
        user_id = request.session.get('user_id')
        if user_id:
            user = CustomUser.objects.get(id=user_id)  # Get the user based on their ID
    except CustomUser.DoesNotExist as e:
        print("User does not exist:", e)
    except Exception as e:
        print("An error occurred:", e)

    return render(request, 'index.html', {"user": user})


def find_jobs(request):
    user = request.user

    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            location = form.cleaned_data['address']
            site_names = request.POST.getlist('job_sites')
            job_preferences = Preference.objects.filter(user=user).values_list('preference', flat=True)

            # 根据信息爬取工作列表
            all_jobs = []
            for preference in job_preferences:
                try:
                    jobs = scrape_jobs(
                        site_name=site_names,
                        search_term=preference,
                        location=location,
                        results_wanted=20,
                        hours_old=72,
                        country_indeed='UK',
                    )
                    all_jobs.append(jobs)
                except ValueError as e:
                    messages.error(request, str(e))
                    return redirect('MainApp:index')  # Redirect to a page to update location

            if all_jobs:
                combined_jobs = pd.concat(all_jobs, ignore_index=True)
                combined_jobs.to_csv(f"static/file/jobs_{user.id}.csv", quoting=csv.QUOTE_NONNUMERIC,
                                     escapechar="\\",
                                     index=False)
            # 这里可以读取用户cv然后结合cv和工作经历筛选工作列表
            return redirect('MainApp:show-jobs')
    else:
        form = CustomUserForm(instance=user)

    context = {'form': form}
    return render(request, 'show_jobs.html', context)


def show_jobs(request):
    user_id = request.user.id
    file_path = f"static/file/jobs_{user_id}.csv"
    cv_objects = CV.objects.filter(user_id=user_id)

    if cv_objects.exists():
        cv_object = cv_objects.first()
        cv_file_path = cv_object.cv_file.path
    if cv_file_path:
        data = ResumeParser(cv_file_path).get_extracted_data()
        skills = data.get('skills', [])

    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        messages.error(request, "No job listings file found or file is empty. Please initiate a search first.")
        return redirect('MainApp:index')
    try:
        jobs = pd.read_csv(file_path)
    except EmptyDataError:
        messages.error(request, "No job found based on your information")
        return redirect('MainApp:index')
    if jobs.empty:
        messages.error(request, "No job listings found in the file.")
        return redirect('MainApp:index')

    matching_jobs = []
    for index, job in jobs.iterrows():
        print(job['description'])

        if not pd.isna(job['description']):
            # Count how many skills are present in the description
            matching_skills = sum(skill.lower() in job['description'].lower() for skill in skills)
            # If most of the skills are present, consider it a matching job
            if matching_skills >= 3:
                matching_jobs.append(job)

    if not matching_jobs:
        messages.error(request, "No matching jobs found based on your skills.")
        return redirect('MainApp:index')

    # Select the columns of interest from matching jobs
    selected_columns = ['site', 'job_url', 'title', 'location', 'is_remote']
    matching_jobs = pd.DataFrame(matching_jobs)[selected_columns]

    context = {
        'jobs': matching_jobs.to_dict('records'),
        'columns': selected_columns
    }
    return render(request, 'show_jobs.html', context)


def favorite_job(request):
    if request.method == 'POST':
        job_url = request.POST.get('job_url')
        title = request.POST.get('title')
        location = request.POST.get('location')
        is_remote = request.POST.get('is_remote')
        is_favorited = request.POST.get('is_favorited')

        # Replace with default values
        if location is None:
            location = "Unknown"

        # Handle is_remote value
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


def profile_view(request):
    user = request.user
    study_instance, _ = Study.objects.get_or_create(user=user)
    experience_instances = Experience.objects.filter(user=user)
    cv_instance, _ = CV.objects.get_or_create(user=user)
    preference_instances = Preference.objects.filter(user=user)

    if request.method == 'POST':
        # Print the path of the CV file

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
            print("CV File Path:", cv_instance.cv_file.path)

            preference_formset.save()
            messages.success(request,
                             'Update your profile successfully.')
            return redirect("MainApp:profile")
    else:
        study_form = StudyForm(instance=study_instance)
        experience_formset = ExperienceFormSet(instance=user, queryset=experience_instances)
        cv_form = CVForm(instance=cv_instance)
        preference_formset = PreferenceFormSet(instance=user, queryset=preference_instances)
        # print(experience_formset)

    context = {
        'study_form': study_form,
        'experience_form': experience_formset,
        'cv_form': cv_form,
        'preference_form': preference_formset,
    }
    return render(request, 'profile.html', context)


def load_file(request, file_name):
    # Remove trailing slash if exists in the path
    file_name = file_name.rstrip('/')
    file_path = os.path.join('MainApp/cvs', file_name)  # Build the file path using relative path

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    else:
        return HttpResponse(f"File not found: {file_path}", status=404)


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

        # Ensure the user has a resume object
        resume, created = Resume.objects.get_or_create(user=user)
        resume.keywords = keywords  # Assume your resume model has a field to store keywords
        resume.save()

        # Redirect to the index page after successful upload
        return HttpResponseRedirect(reverse('index'))
    else:
        # Handle non-POST request or no file uploaded
        return HttpResponse('Invalid request', status=400)


def favorites_view(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        is_favorited = request.POST.get('is_favorited')

        user = request.user
        if is_favorited == 'true':
            # Unfavorite
            FavoriteJob.objects.filter(user=user, id=id).delete()
            # Redirect to favorites page
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
