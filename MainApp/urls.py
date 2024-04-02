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

]
