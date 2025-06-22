from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

from home_server import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('appliances/', include('appliances.urls')),
    path('control/', include('control.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    # Add default login URL pattern
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)