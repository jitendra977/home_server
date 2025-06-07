from django.contrib import admin
from .models import Appliance,Members,Room

@admin.register(Appliance)
class ApplianceAdmin(admin.ModelAdmin):
    list_display = ('name',  'room','status','user')
    list_filter = ('status', 'location')
    search_fields = ('name', 'location')
    
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
	list_display = ('name',)

@admin.register(Members)
class MembersAdmin(admin.ModelAdmin):
    list_display = ('name','phone','email')
    search_fields =('name','phone')
