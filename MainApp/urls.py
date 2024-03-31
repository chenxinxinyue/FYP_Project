from django.urls import path
from . import views
app_name = 'MainApp'

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_view, name='upload'),

]
