# Authentication/urls.py

from django.urls import path
from . import views
from django.urls import path
# from django.contrib.auth import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('password_reset/', views.password_reset_view, name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),


]
