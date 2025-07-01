from django.core.management.base import BaseCommand
from django.conf import settings
import asyncio
from ...services.esphome_discovery import ESPHomeDiscoveryService
import os
from ...models import ESPHomeDevice
from django.utils import timezone

class Command(BaseCommand):
    help = 'Discover ESPHome devices on the network'

    def add_arguments(self, parser):
        parser.add_argument(
            '--network',
            type=str,
            default='192.168.0.0/24',
            help='Network range to scan (default: 192.168.0.0/24)'
        )
        parser.add_argument(
            '--log-file',
            type=str,
            help='Path to ESPHome log file to parse'
        )
        parser.add_argument(
            '--log-content',
            action='store_true',
            help='Parse log content from stdin'
        )

    def handle(self, *args, **options):
        discovery_service = ESPHomeDiscoveryService()
        
        if options['log_file']:
            if not os.path.exists(options['log_file']):
                self.stdout.write(
                    self.style.ERROR(f'Log file not found: {options["log_file"]}')
                )
                return
            
            with open(options['log_file'], 'r') as f:
                log_content = f.read()
            
            self._parse_log_content(discovery_service, log_content)
            
        elif options['log_content']:
            import sys
            log_content = sys.stdin.read()
            self._parse_log_content(discovery_service, log_content)
            
        else:
            self.stdout.write(f'Scanning network {options["network"]} for ESPHome devices...')
            
            loop = asyncio.get_event_loop()
            devices = loop.run_until_complete(
                discovery_service.discover_devices_by_network_scan(options['network'])
            )
            
            self.stdout.write(f'Found {len(devices)} ESPHome devices')
            
            for device_info in devices:
                mac_address = device_info.get("mac_address")
                device_name = device_info.get("name")
                ip_address = device_info.get("ip_address")
                hostname = device_info.get("hostname")
                version = device_info.get("version")
                topic_prefix = device_info.get("mqtt_topic_prefix")
                
                device, created = ESPHomeDevice.objects.update_or_create(
                    mac_address=mac_address,
                    defaults={
                        'name': device_name,
                        'ip_address': ip_address,
                        'hostname': hostname,
                        'version': version,
                        'is_online': True,
                        'mqtt_topic_prefix': topic_prefix,
                        'last_seen': timezone.now(),
                    }
                )
                
                status = "Created" if created else "Updated"
                self.stdout.write(
                    self.style.SUCCESS(f'{status}: {device.name} ({device.ip_address})')
                )
    
    def _parse_log_content(self, discovery_service, log_content):
        parsed_data = discovery_service.parse_esphome_log(log_content)
        
        if not parsed_data["device"]:
            self.stdout.write(
                self.style.WARNING('No device information found in log')
            )
            return
        
        device, created = discovery_service.save_discovered_device(
            parsed_data["device"], 
            parsed_data["sensors"]
        )
        
        status = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f'{status} device: {device.name} with {len(parsed_data["sensors"])} sensors'
            )
        )
        
        self.stdout.write(f'  Name: {device.name}')
        self.stdout.write(f'  IP: {device.ip_address}')
        self.stdout.write(f'  MAC: {device.mac_address}')
        self.stdout.write(f'  Version: {device.version}')
        self.stdout.write(f'  MQTT Prefix: {device.mqtt_topic_prefix}')
        
        if parsed_data["sensors"]:
            self.stdout.write('\n  Sensors:')
            for sensor in parsed_data["sensors"]:
                self.stdout.write(f'    - {sensor["name"]} ({sensor["sensor_type"]})')
                if sensor.get("topic"):
                    self.stdout.write(f'      Topic: {sensor["topic"]}')