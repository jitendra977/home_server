from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('appliances/', include('appliances.urls')),
    path('control/', include('control.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    # Add default login URL pattern
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
]