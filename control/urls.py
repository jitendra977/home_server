from django.urls import path
from . import views

urlpatterns = [
    path('', views.smart_home, name='smart_home'),
]