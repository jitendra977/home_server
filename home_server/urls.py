from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    path('', views.dashboard, name='chart'),
    path('charts/', views.charts, name='chart'),
    path('forms/', views.forms, name='forms'),
    path('icons/', views.icons, name='icons'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('tables/', views.tables, name='tables'),

    
    
    
    
    
    path('admin/', admin.site.urls),
    path('appliances/', include('appliances.urls')),
    path('control/', include('control.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    # Add default login URL pattern
    path('account/login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
]