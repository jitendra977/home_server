# home_server/control/urls.py
from django.urls import path
from . import views

app_name = 'control'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('devices/', views.device_list, name='device_list'),
    path('devices/<int:device_id>/', views.device_detail, name='device_detail'),
    path('devices/<int:device_id>/control/', views.device_control, name='device_control'),
    path('devices/discover/', views.discover_devices, name='discover_devices'),
    path('api/device/<int:device_id>/command/', views.send_command, name='send_command'),
    path('api/devices/status/', views.devices_status, name='devices_status'),
    path('sensors/', views.sensor_list, name='sensor_list'),
    path('sensors/<int:sensor_id>/', views.sensor_detail, name='sensor_detail'),
]