from django.http import HttpResponse

def smart_home(request):
    return HttpResponse("<h2>Smart Home Control App is Live!</h2>")

def toggle_device(request,device_id):
    HttpResponse(f"Device {device_id} is toggled")