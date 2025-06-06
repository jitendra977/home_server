from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('devices/', views.appliance_list, name='appliance_list'),
]