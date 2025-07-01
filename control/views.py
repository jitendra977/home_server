# home_server/control/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
import json
import asyncio
import logging
import threading

from .models import ESPHomeDevice, ESPHomeSensor
from .services.esphome_discovery import ESPHomeDiscoveryService
from .services.mqtt_client import ESPHomeMQTTClient

logger = logging.getLogger(__name__)

mqtt_started = False

def ensure_mqtt_running():
    global mqtt_started
    if not mqtt_started:
        from .services.mqtt_client import ESPHomeMQTTClient
        mqtt_client = ESPHomeMQTTClient()
        thread = threading.Thread(target=mqtt_client.connect_and_loop, daemon=True)
        thread.start()
        mqtt_started = True

def dashboard(request):
    ensure_mqtt_running()
    """Main dashboard view"""
    context = {
        'total_devices': ESPHomeDevice.objects.count(),
        'online_devices': ESPHomeDevice.objects.filter(is_online=True).count(),
        'total_sensors': ESPHomeSensor.objects.count(),
        'recent_devices': ESPHomeDevice.objects.order_by('-last_seen')[:5],
        'controllable_sensors': ESPHomeSensor.objects.filter(is_controllable=True)[:10],
        'sensor_types': ESPHomeSensor.objects.values('sensor_type').annotate(
            count=Count('sensor_type')
        ).order_by('sensor_type'),
    }
    
    # Get devices by status
    context['offline_devices'] = ESPHomeDevice.objects.filter(is_online=False).count()
    
    return render(request, 'control/dashboard.html', context)

def device_list(request):
    """List all ESPHome devices"""
    devices = ESPHomeDevice.objects.all().prefetch_related('sensors')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        devices = devices.filter(
            Q(name__icontains=search_query) |
            Q(hostname__icontains=search_query) |
            Q(ip_address__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter == 'online':
        devices = devices.filter(is_online=True)
    elif status_filter == 'offline':
        devices = devices.filter(is_online=False)
    
    # Pagination
    paginator = Paginator(devices, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'control/device_list.html', context)

def device_detail(request, device_id):
    """Device detail view with sensors"""
    device = get_object_or_404(ESPHomeDevice, id=device_id)
    sensors = device.sensors.all().order_by('sensor_type', 'name')
    
    # Group sensors by type
    sensor_groups = {}
    for sensor in sensors:
        if sensor.sensor_type not in sensor_groups:
            sensor_groups[sensor.sensor_type] = []
        sensor_groups[sensor.sensor_type].append(sensor)
    
    context = {
        'device': device,
        'sensors': sensors,
        'sensor_groups': sensor_groups,
        'controllable_sensors': sensors.filter(is_controllable=True),
    }
    
    return render(request, 'control/device_detail.html', context)

def device_control(request, device_id):
    """Device control interface"""
    device = get_object_or_404(ESPHomeDevice, id=device_id)
    controllable_sensors = device.sensors.filter(is_controllable=True)
    
    context = {
        'device': device,
        'controllable_sensors': controllable_sensors,
    }
    
    return render(request, 'control/device_control.html', context)

@csrf_exempt
def send_command(request, device_id):
    """Send command to device via MQTT"""
    if request.method == "POST":
        try:
            if request.content_type == "application/json":
                data = json.loads(request.body)
                sensor_name = data.get("sensor_name")
                command = data.get("command")
            else:
                sensor_name = request.POST.get("sensor_name")
                command = request.POST.get("command")
            
            if not sensor_name or command is None:
                return JsonResponse({
                    'success': False, 
                    'error': 'Missing sensor_name or command'
                })
            
            # Initialize MQTT client
            mqtt_client = ESPHomeMQTTClient()
            # Find device to get topic_prefix
            device = ESPHomeDevice.objects.get(id=device_id)
            ok = mqtt_client.publish_command(device.mqtt_topic_prefix, sensor_name, command)
            return JsonResponse({'success': ok})
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

def discover_devices(request):
    """Discover ESPHome devices on network"""
    if request.method == 'POST':
        network_range = request.POST.get('network_range', '192.168.0.0/24')
        
        try:
            discovery_service = ESPHomeDiscoveryService()
            
            # Run discovery
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            devices = loop.run_until_complete(
                discovery_service.discover_devices_by_network_scan(network_range)
            )
            loop.close()
            
            # Save discovered devices
            created_count = 0
            updated_count = 0
            
            for device_info in devices:
                device, created = discovery_service.save_discovered_device(
                    device_info, []
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            messages.success(
                request, 
                f'Discovery complete! Created {created_count} new devices, '
                f'updated {updated_count} existing devices.'
            )
            
        except Exception as e:
            logger.error(f"Discovery error: {e}")
            messages.error(request, f'Discovery failed: {str(e)}')
        
        return redirect('control:device_list')
    
    return render(request, 'control/discover_devices.html')

def devices_status(request):
    """API endpoint for device status updates"""
    devices = ESPHomeDevice.objects.all().values(
        'id', 'name', 'is_online', 'last_seen', 'wifi_signal'
    )
    
    return JsonResponse({
        'devices': list(devices),
        'timestamp': timezone.now().isoformat()
    })

def sensor_list(request):
    """List all sensors"""
    sensors = ESPHomeSensor.objects.select_related('device').all()
    
    # Filter by sensor type
    sensor_type = request.GET.get('type')
    if sensor_type:
        sensors = sensors.filter(sensor_type=sensor_type)
    
    # Filter by device
    device_id = request.GET.get('device')
    if device_id:
        sensors = sensors.filter(device_id=device_id)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        sensors = sensors.filter(
            Q(name__icontains=search_query) |
            Q(device__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(sensors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'sensor_types': ESPHomeSensor.SENSOR_TYPES,
        'devices': ESPHomeDevice.objects.all(),
        'current_type': sensor_type,
        'current_device': device_id,
        'search_query': search_query,
    }
    
    return render(request, 'control/sensor_list.html', context)

def sensor_detail(request, sensor_id):
    """Sensor detail view"""
    sensor = get_object_or_404(ESPHomeSensor, id=sensor_id)
    
    context = {
        'sensor': sensor,
    }
    
    return render(request, 'control/sensor_detail.html', context)

