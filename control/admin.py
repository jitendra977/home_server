from django.contrib import admin
from .models import ESPHomeDevice, ESPHomeSensor

@admin.register(ESPHomeDevice)
class ESPHomeDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'is_online', 'last_seen')
    search_fields = ('name', 'ip_address', 'mac_address')

@admin.register(ESPHomeSensor)
class ESPHomeSensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'sensor_type', 'device', 'last_value', 'last_updated')
    search_fields = ('name', 'device__name')
    list_filter = ('sensor_type',)
