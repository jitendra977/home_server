from django.contrib import admin
from .models import Appliance, Room



@admin.register(Appliance)
class ApplianceAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'device_type', 
        'room', 
        'status', 
        'is_active', 
        'user', 
        'created_at', 
        'updated_at'
    )
    list_filter = (
        'device_type', 
        'status', 
        'is_active', 
        'room', 
        'user'
    )
    search_fields = ('name', 'location', 'device_type')
    ordering = ('-updated_at',)

    # Optional: show fewer fields while creating/editing if you want
    fieldsets = (
        (None, {
            'fields': ('name', 'device_type', 'location', 'room', 'user')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Timestamps (Read Only)', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'floor', 'owner', 'created_at')
    search_fields = ('name', 'floor')
    list_filter = ('floor', 'owner')