from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('devices/', views.appliance_list, name='appliance_list'),
    path('devices/edit/<int:pk>/', views.appliance_edit, name='appliance_edit'),
    path('devices/delete/<int:pk>/', views.appliance_delete, name='appliance_delete'),
    path('api/rooms/', views.get_rooms, name='api_rooms'),
    path('api/users/', views.get_users, name='api_users'),
]