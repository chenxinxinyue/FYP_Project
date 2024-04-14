import pandas as pd
from celery.result import AsyncResult
from django.core.management import call_command
from django.http import HttpResponseRedirect, FileResponse, HttpResponse, JsonResponse
from django.urls import reverse
from Authentication.forms import CustomUserForm
from .models import Job, School, CustomUser, Study, Experience, CV, Preference, Resume, FavoriteJob
from .utils import extract_keywords
from django.shortcuts import render, redirect
from .forms import StudyForm, ExperienceForm, CVForm, PreferenceForm, ExperienceFormSet, PreferenceFormSet
from django.contrib import messages
import os


def index(request):
    user = None  # Initialize the user variable here

    try:
        user_id = request.session.get('user_id')

        if user_id:
            # Get the user based on their ID
            user = CustomUser.objects.get(id=user_id)

    except CustomUser.DoesNotExist as e:
        print("User does not exist:", e)
    except Exception as e:
        print("An error occurred:", e)
    countries = [
        "US/CA","WorldWide","Argentina", "Australia*", "Austria*", "Bahrain", "Belgium*", "Brazil*", "Canada*", "Chile",
        "China", "Colombia", "Costa Rica", "Czech Republic", "Denmark", "Ecuador", "Egypt", "Finland",
        "France*", "Germany*", "Greece", "Hong Kong*", "Hungary", "India*", "Indonesia", "Ireland*",
        "Israel", "Italy*", "Japan", "Kuwait", "Luxembourg", "Malaysia", "Mexico*", "Morocco",
        "Netherlands*", "New Zealand*", "Nigeria", "Norway", "Oman", "Pakistan", "Panama", "Peru",
        "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Saudi Arabia", "Singapore*",
        "South Africa", "South Korea", "Spain*", "Sweden", "Switzerland*", "Taiwan", "Thailand",
        "Turkey", "Ukraine", "United Arab Emirates", "UK*", "USA*", "Uruguay", "Venezuela", "Vietnam*"
    ]
    return render(request, 'index.html', {"user": user, "countries": countries})


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


def load_file(request, file_name):
    # Remove trailing slash if exists in the path
    file_name = file_name.rstrip('/')
    file_path = os.path.join('MainApp/cvs', file_name)  # Build the file path using relative path

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    else:
        return HttpResponse(f"File not found: {file_path}", status=404)


def find_jobs(request):
    user = request.user

    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            location = form.cleaned_data['address']
            site_names = request.POST.getlist('job_sites')
            country_indeed = request.POST.get('country')
            country_indeed = country_indeed.replace('*', '')

            if not site_names:
                site_names = ["indeed", "linkedin", "zip_recruiter", "glassdoor"]
            if not location:
                messages.error(request, 'Please enter your location')
                return redirect('MainApp:index')
            job_preferences = Preference.objects.filter(user=user).values_list('preference', flat=True)
            job_preferences_list = list(job_preferences)
            if not job_preferences_list:
                messages.error(request, 'Preference cannot be empty. Please complete your profile')
                return redirect('MainApp:index')
            call_command('job_scraper', location, job_preferences=job_preferences_list, user_id=user.id,
                         site_names=site_names, country_indeed=country_indeed)

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
