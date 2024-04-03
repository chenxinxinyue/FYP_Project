from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from Authentication.models import Resume, CustomUser  # 确保正确导入 Resume 模型
from .models import Job  # 确保正确导入 Resume 模型
from .utils import extract_keywords  # 假设你有一个工具函数来提取简历中的关键词
from django.shortcuts import render, redirect
from Authentication.forms import StudyForm, ExperienceForm, CVForm, PreferenceForm
from Authentication.models import CustomUser, Study, Experience, CV, Preference

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


def profile_view(request):
    # Try to get the user instance from the session
    user = None
    try:
        user_id = request.session.get('user_id')
        if user_id:
            user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return HttpResponse("User does not exist.", status=404)

    # initial forms
    if user:
        # Retrieve existing data from the database and create an empty instance
        # if it is not present
        study, _ = Study.objects.get_or_create(user=user)
        experiences = Experience.objects.filter(user=user)
        cv, _ = CV.objects.get_or_create(user=user)
        preferences = Preference.objects.filter(user=user)

        study_form = StudyForm(request.POST or None, instance=study)
        experience_forms = [ExperienceForm(request.POST or None, instance=experience) for experience in experiences]
        cv_form = CVForm(request.POST or None, request.FILES or None, instance=cv)
        preference_forms = [PreferenceForm(request.POST or None, instance=preference) for preference in preferences]

        # If it's a POST request, process the form data
        if request.method == 'POST':
            if (study_form.is_valid() and
                    all([form.is_valid() for form in experience_forms]) and
                    cv_form.is_valid() and
                    all([form.is_valid() for form in preference_forms])):

                study_form.save()

                for form in experience_forms:
                    experience = form.save(commit=False)
                    experience.user = user
                    experience.save()

                cv_form.save()

                for form in preference_forms:
                    preference = form.save(commit=False)
                    preference.user = user
                    preference.save()

                return redirect('MainApp:index')

    else:
        return redirect('MainApp:login')

    context = {
        'study_form': study_form,
        'experience_forms': experience_forms,
        'cv_form': cv_form,
        'preference_forms': preference_forms
    }
    return render(request, 'profile.html', context)


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


def jobs_view(request):
    jobs = Job.objects.all()
    return render(request, 'jobs.html', {'jobs': jobs})
