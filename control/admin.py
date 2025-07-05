from django.contrib import admin
from .models import ESPHomeDevice, ESPHomeSensor  # Make sure this matches your models.py

@admin.register(ESPHomeDevice)
class ESPHomeDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'is_online', 'last_seen')
    search_fields = ('name', 'ip_address', 'mac_address')

@admin.register(ESPHomeSensor)
class ESPHomeSensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'device', 'sensor_type', 'last_value')
    list_filter = ('sensor_type', 'device')