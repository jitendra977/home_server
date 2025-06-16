from django.urls import path
from . import views

app_name = 'control'  # Add namespace

urlpatterns = [
    path('', views.smart_home, name='smart_home'),
    path('toggle/<int:device_id>/', views.toggle_device, name='toggle_device'),
]