from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .forms import ApplianceForm
from .models import Appliance,Room
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from django.db.models import Count
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps

def home_page(request):
    return render(request, 'appliances/home.html')  

def superuser_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "Permission denied. Only superusers can perform this action.")
            return redirect('appliance_list')
    return wrap
@login_required
def appliance_list(request):
    # 👉 Superuser sees all, user sees only own
    if request.user.is_superuser:
        appliances = Appliance.objects.all()
    else:
        appliances = Appliance.objects.filter(user=request.user)

    form = None  # default: no form

    if request.user.is_superuser:
        # ✅ Only superuser can access form and submit
        form = ApplianceForm(request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                appliance = form.save(commit=False)
                appliance.user = request.user
                appliance.save()
                messages.success(request, 'Device added successfully!')
                return redirect('appliance_list')
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        # ❌ Prevent normal user from submitting POST even by API tools like Postman
        if request.method == 'POST':
            messages.error(request, "Permission denied. Only superusers can add devices.")
            return redirect('appliance_list')

    context = {
        'form': form,
        'appliances': appliances,
        'total_devices': appliances.count(),
        'total_room': Room.objects.count(),
        'total_rooms': Room.objects.count(),
        'rooms_with_devices': Room.objects.annotate(
            device_count=Count('appliances')
        ).filter(device_count__gt=0).count(),
    }
    return render(request, 'appliances/device_list.html', context)
@login_required
@superuser_required
def appliance_edit(request, pk):
    appliance = get_object_or_404(Appliance, pk=pk)
    form = ApplianceForm(request.POST or None, instance=appliance)
    if form.is_valid():
        form.save()
        return redirect('appliance_list')
    return render(request, 'appliances/device_form.html', {'form': form})

@login_required
@superuser_required
def appliance_new(request):
    form = ApplianceForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('appliance_list')
    return render(request, 'appliances/device_form.html', {'form': form})

@login_required
@superuser_required
def appliance_delete(request, pk):
    appliance = get_object_or_404(Appliance, pk=pk)
    if request.method == 'POST':
        appliance.delete()
        return redirect('appliance_list')
    return render(request, 'appliances/device_confirm_delete.html', {'appliance': appliance})

