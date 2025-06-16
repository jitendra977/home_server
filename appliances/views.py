from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .forms import ApplianceForm
from .models import Appliance,Room
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from django.db.models import Count

def home_page(request):
    return render(request, 'appliances/home.html')  

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
        'total_rooms': rooms_with_devices.count(),  # Only count rooms with devices
        'active_rooms': active_rooms.count(),
    }
    return render(request, 'appliances/device_list.html', context)  # Template र context पठाउने
@login_required
def appliance_edit(request, pk):
    appliance = get_object_or_404(Appliance, pk=pk)
    form = ApplianceForm(request.POST or None, instance=appliance)
    if form.is_valid():
        form.save()
        return redirect('appliance_list')
    return render(request, 'appliances/device_form.html', {'form': form})

@login_required
def appliance_delete(request, pk):
    appliance = get_object_or_404(Appliance, pk=pk)
    if request.method == 'POST':
        appliance.delete()
        return redirect('appliance_list')
    return render(request, 'appliances/device_confirm_delete.html', {'appliance': appliance})

@login_required
def device_new(request):
    if request.method == "POST":
        form = ApplianceForm(request.POST)  # Change DeviceForm to ApplianceForm
        if form.is_valid():
            device = form.save()
            messages.success(request, 'Device added successfully!')
            return redirect('device_list')
    else:
        form = ApplianceForm()  # Change DeviceForm to ApplianceForm
    return render(request, 'appliances/device_form.html', {'form': form})

