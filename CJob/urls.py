from django.urls import path
from . import views
app_name = 'CJob'

urlpatterns = [
    path('', views.home, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
]
