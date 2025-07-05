from django.core.management.base import BaseCommand
from django.conf import settings
import asyncio
from ...services.esphome_discovery import ESPHomeDiscoveryService
import os
from ...models import ESPHomeDevice
from django.utils import timezone
from django.db import transaction

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
        parser.add_argument(
            '--cleanup-duplicates',
            action='store_true',
            help='Clean up existing duplicate devices'
        )

    def handle(self, *args, **options):
        discovery_service = ESPHomeDiscoveryService()
        
        if options['cleanup_duplicates']:
            self._cleanup_duplicate_devices()
            return
            
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
            
            # Fixed: Extract sensors from each device_info properly
            for device_info in devices:
                sensors = device_info.get("sensors", [])  # Get sensors from discovery
                
                # Debug output to check what we have
                self.stdout.write(f'Processing device: {device_info.get("name", "Unknown")}')
                self.stdout.write(f'  IP: {device_info.get("ip_address", "Unknown")}')
                self.stdout.write(f'  Found {len(sensors)} sensors')
                
                # Save the device with its sensors
                device, created = discovery_service.save_discovered_device(device_info, sensors)
                
                if device:
                    status = "Created" if created else "Updated"
                    self.stdout.write(
                        self.style.SUCCESS(f'{status}: {device.name} ({device.ip_address}) with {len(sensors)} sensors')
                    )
                    
                    # List the sensors that were found
                    if sensors:
                        self.stdout.write('  Sensors:')
                        for sensor in sensors:
                            self.stdout.write(f'    - {sensor.get("name", "Unknown")} ({sensor.get("sensor_type", "unknown")})')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Failed to save device: {device_info.get("name", "Unknown")}')
                    )
    
    def _cleanup_duplicate_devices(self):
        """Clean up existing duplicate devices in the database"""
        self.stdout.write("Cleaning up duplicate ESPHome devices...")
        
        # Get all devices
        all_devices = ESPHomeDevice.objects.all()
        
        # Group potential duplicates
        device_groups = {}
        
        for device in all_devices:
            # Create a key based on potential matching criteria
            key_parts = []
            
            if device.mac_address:
                key_parts.append(f"mac:{device.mac_address}")
            if device.ip_address and device.ip_address != "0.0.0.0":
                key_parts.append(f"ip:{device.ip_address}")
            if device.hostname:
                key_parts.append(f"host:{device.hostname}")
            
            # Also check for name-based matches (KITCHEN vs ESPHome_192_168_0_67)
            if device.name:
                clean_name = device.name.lower().replace('_', '').replace('-', '')
                key_parts.append(f"name:{clean_name}")
                
                # If it's an IP-based name, also add the IP as a key
                if device.name.startswith('ESPHome_') and device.ip_address != "0.0.0.0":
                    ip_suffix = device.ip_address.replace('.', '_')
                    key_parts.append(f"ip_name:{ip_suffix}")
            
            # Create composite key
            if key_parts:
                key = "|".join(sorted(key_parts))
                if key not in device_groups:
                    device_groups[key] = []
                device_groups[key].append(device)
        
        # Now check for cross-references (e.g., KITCHEN might match ESPHome_192_168_0_67)
        merged_groups = {}
        processed_devices = set()
        
        for device in all_devices:
            if device.id in processed_devices:
                continue
                
            group = [device]
            processed_devices.add(device.id)
            
            # Find all devices that might be the same as this one
            for other_device in all_devices:
                if other_device.id in processed_devices:
                    continue
                    
                is_match = False
                
                # Check if they share MAC address
                if device.mac_address and other_device.mac_address and device.mac_address == other_device.mac_address:
                    is_match = True
                
                # Check if they share IP address (and it's not 0.0.0.0)
                elif device.ip_address and other_device.ip_address and device.ip_address != "0.0.0.0" and device.ip_address == other_device.ip_address:
                    is_match = True
                
                # Check if they share hostname
                elif device.hostname and other_device.hostname and device.hostname == other_device.hostname:
                    is_match = True
                
                # Check special case: name-based matching (KITCHEN vs ESPHome_192_168_0_67)
                elif device.name and other_device.name:
                    # If one has a real name and the other has IP-based name
                    if (not device.name.startswith('ESPHome_') and other_device.name.startswith('ESPHome_') and 
                        device.ip_address != "0.0.0.0" and other_device.ip_address != "0.0.0.0"):
                        # Check if IPs match
                        if device.ip_address == other_device.ip_address:
                            is_match = True
                    elif (device.name.startswith('ESPHome_') and not other_device.name.startswith('ESPHome_') and 
                          device.ip_address != "0.0.0.0" and other_device.ip_address != "0.0.0.0"):
                        # Check if IPs match
                        if device.ip_address == other_device.ip_address:
                            is_match = True
                
                if is_match:
                    group.append(other_device)
                    processed_devices.add(other_device.id)
            
            if len(group) > 1:
                merged_groups[device.id] = group
        
        # Merge duplicate groups
        for primary_id, group in merged_groups.items():
            if len(group) <= 1:
                continue
                
            # Find the best device to keep (prefer one with real name and valid IP)
            best_device = None
            for device in group:
                if not best_device:
                    best_device = device
                elif (device.ip_address != "0.0.0.0" and best_device.ip_address == "0.0.0.0"):
                    best_device = device
                elif (device.name and not device.name.startswith('ESPHome_') and 
                      best_device.name and best_device.name.startswith('ESPHome_')):
                    best_device = device
                elif device.mac_address and not best_device.mac_address:
                    best_device = device
            
            # Merge information from other devices into the best one
            for device in group:
                if device.id == best_device.id:
                    continue
                    
                # Update best_device with any missing information
                if not best_device.name or best_device.name.startswith('ESPHome_'):
                    if device.name and not device.name.startswith('ESPHome_'):
                        best_device.name = device.name
                
                if not best_device.mac_address and device.mac_address:
                    best_device.mac_address = device.mac_address
                
                if (not best_device.ip_address or best_device.ip_address == "0.0.0.0") and device.ip_address and device.ip_address != "0.0.0.0":
                    best_device.ip_address = device.ip_address
                
                if not best_device.hostname and device.hostname:
                    best_device.hostname = device.hostname
                
                if not best_device.version and device.version:
                    best_device.version = device.version
                
                if not best_device.mqtt_topic_prefix and device.mqtt_topic_prefix:
                    best_device.mqtt_topic_prefix = device.mqtt_topic_prefix
            
            # Save the merged device
            best_device.save()
            
            # Delete the duplicates
            devices_to_delete = [d for d in group if d.id != best_device.id]
            for device in devices_to_delete:
                self.stdout.write(f"Deleting duplicate: {device.name} ({device.ip_address})")
                device.delete()
            
            self.stdout.write(
                self.style.SUCCESS(f"Merged {len(group)} devices into: {best_device.name} ({best_device.ip_address})")
            )
        
        self.stdout.write("Cleanup completed!")
    
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