from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ApplianceForm
from .models import Appliance

def home_page(request):
    return render(request, 'appliances/home.html')  
    
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