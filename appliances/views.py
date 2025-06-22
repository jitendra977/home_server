from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .forms import ApplianceForm
from .models import Appliance, Room
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from django.db.models import Count, Q
from functools import wraps

def home_page(request):
    return render(request, 'appliances/home.html')  

def superuser_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        # यदि प्रयोगकर्ता superuser छैन भने, अनुमति अस्वीकृत सन्देश देखाएर उपकरणहरूको सूचीमा फर्काउँछ।
        if not request.user.is_superuser:
            messages.error(request, "Permission denied. Only superusers can perform this action.")
            return redirect('appliance_list')
        # यदि प्रयोगकर्ता superuser हो भने, मूल प्रकार्य (original function) चलाउँछ।
        return function(request, *args, **kwargs)
    return wrap

@login_required
def appliance_list(request):
    # For superusers, show all devices
    if request.user.is_superuser:
        appliances = Appliance.objects.all()
        rooms_with_devices = Room.objects.filter(appliances__isnull=False).distinct()
        active_rooms = Room.objects.filter(appliances__status=True).distinct()
    else:
        # For regular users, show:
        # 1. Devices in their owned rooms
        # 2. Devices assigned to them personally (if any)
        user_rooms = Room.objects.filter(owner=request.user)
        appliances = Appliance.objects.filter(
            Q(room__in=user_rooms) | 
            Q(user=request.user)
        ).distinct()
        
        rooms_with_devices = user_rooms.filter(appliances__isnull=False).distinct()
        active_rooms = user_rooms.filter(appliances__status=True).distinct()
    
    context = {
        'appliances': appliances,
        'total_devices': appliances.count(),
        'active_devices': appliances.filter(status=True).count(),
        'inactive_devices': appliances.filter(status=False).count(),
        'total_rooms': rooms_with_devices.count(),
        'active_rooms': active_rooms.count(),
        'form': ApplianceForm(user=request.user),
        'is_superuser': request.user.is_superuser,
    }
    return render(request, 'appliances/device_list.html', context)
@login_required
@superuser_required
def appliance_edit(request, pk):
    appliance = get_object_or_404(Appliance, pk=pk)
    if request.method == 'POST':
        form = ApplianceForm(request.POST, instance=appliance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Device updated successfully!')
            return redirect('appliance_list')
    else:
        form = ApplianceForm(instance=appliance)
    return render(request, 'appliances/device_form.html', {'form': form})

@login_required
@superuser_required
def appliance_delete(request, pk):
    appliance = get_object_or_404(Appliance, pk=pk)
    if request.method == 'POST':
        appliance.delete()
        messages.success(request, 'Device deleted successfully!')
        return redirect('appliance_list')
    return render(request, 'appliances/device_confirm_delete.html', {'appliance': appliance})

@login_required
@superuser_required
def device_new(request):
    if request.method == 'POST':
        form = ApplianceForm(request.POST, user=request.user)  # Pass user to form
        if form.is_valid():
            appliance = form.save()
            
            # Handle AJAX response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': 'Device added successfully!',
                    'device': {
                        'id': appliance.id,
                        'name': appliance.name,
                        'type': appliance.get_device_type_display(),
                        'status': appliance.status
                    }
                })
            
            messages.success(request, 'Device added successfully!')
            return redirect('appliance_list')
        
        # Form is invalid
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {
                field: {
                    'message': error.as_text(),
                    'id': form[field].id_for_label
                } 
                for field, error in form.errors.items()
            }
            return JsonResponse({
                'success': False, 
                'errors': errors,
                'message': 'Please correct the errors below.'
            }, status=400)
        
        # Non-AJAX form submission with errors
        messages.error(request, 'Please correct the errors below.')
        return render(request, 'appliances/device_list.html', {
            'form': form,
            'show_modal': True,
            **get_device_stats_context()  # Include stats for page reload
        })

    # GET request - initialize form
    form = ApplianceForm(user=request.user)
    
    # For AJAX GET requests (e.g., loading modal content)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'modal_html': render_to_string('appliances/partials/add_device_modal.html', {
                'form': form
            }, request=request)
        })
    
    # Regular GET request - show full page
    return render(request, 'appliances/device_list.html', {
        'form': form,
        **get_device_stats_context()
    })

def get_device_stats_context():
    """Helper function to get device statistics for the context"""
    appliances = Appliance.objects.all()
    rooms = Room.objects.all()
    
    return {
        'appliances': appliances,
        'total_devices': appliances.count(),
        'active_devices': appliances.filter(status=True).count(),
        'inactive_devices': appliances.filter(status=False).count(),
        'total_rooms': rooms.count(),
        'active_rooms': rooms.filter(appliances__status=True).distinct().count(),
    }