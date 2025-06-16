import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from appliances.models import Appliance

def smart_home(request):
    return HttpResponse("<h2>Smart Home Control App is Live!</h2>")

@require_http_methods(["POST"])
def toggle_device(request, device_id):
    try:
        data = json.loads(request.body)
        device = Appliance.objects.get(id=device_id)
        device.status = data.get('status', False)
        device.save()
        return JsonResponse({
            'success': True,
            'status': device.status
        })
    except Appliance.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Device with ID {device_id} not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
