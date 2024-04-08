from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

app_name = 'MainApp'

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_view, name='upload'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('profile/', views.profile_view, name='profile'),
    path('jobs/', views.jobs_view, name='jobs'),
    path('cvs/<str:file_name>/', views.load_file, name='load_file'),
    path('get-schools/', views.get_schools, name='get-schools'),
    path('get-jobs/', views.get_jobs, name='get-jobs'),
    path('find_jobs/', views.find_jobs, name='find-jobs'),
    path('show_jobs/', views.show_jobs, name='show-jobs'),
    path('favorite_job/', views.favorite_job, name='favorite-job'),
    # path('favorite-job/<int:job_id>/', views.favorite_job, name='favorite-job'),

]
