from django.contrib import admin
from .models import Appliance,Members

@admin.register(Appliance)
class ApplianceAdmin(admin.ModelAdmin):
    list_display = ('name',  'location','status')
    list_filter = ('status', 'location')
    search_fields = ('name', 'location')
   
@admin.register(Members)
class MembersAdmin(admin.ModelAdmin):
    list_display = ('name','phone','email')
    search_fields =('name','phone')
