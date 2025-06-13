from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .forms import ApplianceForm
from .models import Appliance
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

def home_page(request):
    return render(request, 'appliances/home.html')  

@login_required
def appliance_list(request):
    appliances = Appliance.objects.all()  # सबै डिभा1इस ल्याउने
    form = ApplianceForm(request.POST or None)  # Form data लिने

    if request.method == 'POST':  # Form सबमिट भएमा
        if form.is_valid():  # डाटा ठिक भएमा
            form.save()  # नयाँ डिभाइस save गर्ने
            messages.success(request, 'Device added successfully!')
            return redirect('appliance_list')  # फेरी लिस्ट पेजमा फर्किने
        else:
            messages.error(request, 'Please correct the errors below.')

    context = {
        'form': form,
        'appliances': appliances,
        'total_devices': appliances.count()
    }
    return render(request, 'appliances/device_list.html', context)  # Template र context पठाउने
def appliance_edit(request, pk):
    appliance = get_object_or_404(Appliance, pk=pk)
    form = ApplianceForm(request.POST or None, instance=appliance)
    if form.is_valid():
        form.save()
        return redirect('appliance_list')
    return render(request, 'appliances/device_form.html', {'form': form})

def appliance_delete(request, pk):
    appliance = get_object_or_404(Appliance, pk=pk)
    if request.method == 'POST':
        appliance.delete()
        return redirect('appliance_list')
    return render(request, 'appliances/device_confirm_delete.html', {'appliance': appliance})

@require_http_methods(["POST"])
def toggle_device_status(request, device_id):
    try:
        device = Appliance.objects.get(id=device_id)
        data = json.loads(request.body)
        device.status = data.get('status', False)
        device.save()
        return JsonResponse({'success': True})
    except Appliance.DoesNotExist:
        return JsonResponse({'error': 'Device not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)