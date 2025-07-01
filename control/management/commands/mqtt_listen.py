from django.core.management.base import BaseCommand
from ...services.mqtt_client import ESPHomeMQTTClient
import signal
import sys

class Command(BaseCommand):
    help = 'Start MQTT listener for ESPHome devices'

    def handle(self, *args, **options):
        mqtt_client = ESPHomeMQTTClient()
        
        def signal_handler(sig, frame):
            self.stdout.write(self.style.WARNING('\nDisconnecting from MQTT broker...'))
            mqtt_client.disconnect()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        self.stdout.write(
            self.style.SUCCESS('Starting MQTT listener (press Ctrl+C to exit)')
        )
        
        try:
            mqtt_client.connect_and_loop()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nReceived keyboard interrupt. Shutting down...'))
            mqtt_client.disconnect()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error in MQTT listener: {e}')
            )
            mqtt_client.disconnect()