from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .forms import ApplianceForm
from .models import Appliance, Room
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from django.db.models import Count
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
    appliances = Appliance.objects.all()
    
    # Get rooms that have at least one device
    rooms_with_devices = Room.objects.filter(appliances__isnull=False).distinct()
    
    # Get rooms that have at least one active device
    active_rooms = Room.objects.filter(appliances__status=True).distinct()
    
    context = {
        'appliances': appliances,
        'total_devices': appliances.count(),
        'active_devices': appliances.filter(status=True).count(),
        'inactive_devices': appliances.filter(status=False).count(),
        'total_rooms': rooms_with_devices.count(),
        'active_rooms': active_rooms.count(),
        'form': ApplianceForm()  # Add empty form to context for the modal
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
    # This block handles both initial GET request and POST request for form submission
    if request.method == 'POST':
        form = ApplianceForm(request.POST)
        if form.is_valid():
            appliance = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Device added successfully!'})
            return redirect('appliance_list') # Fallback for non-AJAX submission
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Prepare errors for JSON response
                errors = {}
                for field, field_errors in form.errors.items():
                    # For non_field_errors, field will be '__all__'
                    if field == '__all__':
                        errors['non_field_errors'] = [str(e) for e in field_errors]
                    else:
                        errors[field] = {
                            'message': str(field_errors.as_text()), # Get the error message
                            'id': form[field].id_for_label # Get the ID for the corresponding input field
                        }
                return JsonResponse({'success': False, 'errors': errors}, status=400) # Send 400 Bad Request status
            # Fallback for non-AJAX submission with errors
            # If not AJAX, you'd typically re-render the template with the form and its errors
            # return render(request, 'your_template_name.html', {'form': form})
            # Or in your case, you might reload the main device list page with the modal showing errors
            return render(request, 'appliance_list.html', {'form': form, 'show_modal_with_errors': True}) # Pass form and flag

    else: # GET request
        form = ApplianceForm()

    # This context is for the initial load of the device list page
    # You'll need to ensure 'appliances', 'total_devices', etc. are available here
    # This might require fetching them from your models
    appliances = Appliance.objects.all() # Example
    total_devices = Appliance.objects.count()
    active_devices = Appliance.objects.filter(status=True).count()
    inactive_devices = total_devices - active_devices
    total_rooms = Room.objects.count()
    active_rooms = Room.objects.filter(appliance__status=True).distinct().count() # Example logic for active rooms

    context = {
        'form': form,
        'appliances': appliances,
        'total_devices': total_devices,
        'active_devices': active_devices,
        'inactive_devices': inactive_devices,
        'total_rooms': total_rooms,
        'active_rooms': active_rooms,
    }
    # If using a Class-Based View, this logic would be in form_valid and form_invalid methods.
    return render(request, 'appliance_list.html', context)