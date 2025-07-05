import asyncio
import aiohttp
import json
import re
import socket
from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from django.conf import settings
from ..models import ESPHomeDevice, ESPHomeSensor
import logging

logger = logging.getLogger(__name__)

class ESPHomeDiscoveryService:
    def __init__(self):
        self.discovered_devices = {}
        self.mqtt_broker = getattr(settings, 'MQTT_BROKER_HOST', '192.168.0.59')
        self.mqtt_port = getattr(settings, 'MQTT_BROKER_PORT', 1883)
    
    async def discover_devices_by_network_scan(self, network_range: str = "192.168.0.0/24"):
        """Discover ESPHome devices by scanning network range"""
        import ipaddress
        
        try:
            network = ipaddress.IPv4Network(network_range, strict=False)
        except ValueError as e:
            logger.error(f"Invalid network range {network_range}: {e}")
            return []
        
        logger.info(f"Scanning network {network_range} for ESPHome devices...")
        tasks = []
        semaphore = asyncio.Semaphore(50)  # Limit concurrent connections
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5),  # Increased timeout
            connector=aiohttp.TCPConnector(limit=100)
        ) as session:
            for ip in network.hosts():
                tasks.append(self._check_esphome_device_with_semaphore(semaphore, session, str(ip)))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
        # Filter out exceptions and None results
        devices = []
        for result in results:
            if isinstance(result, dict) and result:
                devices.append(result)
            elif isinstance(result, Exception):
                logger.debug(f"Discovery exception: {result}")
                
        logger.info(f"Found {len(devices)} ESPHome devices")
        return devices
    
    async def _check_esphome_device_with_semaphore(self, semaphore, session, ip):
        async with semaphore:
            return await self._check_esphome_device(session, ip)
    
    async def _check_esphome_device(self, session: aiohttp.ClientSession, ip: str) -> Optional[Dict]:
        """Check if device at IP is an ESPHome device"""
        try:
            # First check if port 80 is open
            if not await self._check_port(ip, 80):
                return None
            
            # Try to get the main page
            async with session.get(f"http://{ip}/", 
                                 allow_redirects=True,
                                 headers={'User-Agent': 'ESPHome-Discovery/1.0'}) as response:
                if response.status == 200:
                    text = await response.text()
                    
                    # Check for ESPHome indicators
                    esphome_indicators = [
                        "ESPHome",
                        "esphome",
                        "ESP8266",
                        "ESP32",
                        "device-info",
                        "webserver"
                    ]
                    
                    if any(indicator in text for indicator in esphome_indicators):
                        logger.info(f"Found potential ESPHome device at {ip}")
                        device_info = await self._get_device_info(session, ip, text)
                        if device_info:
                            return device_info
                        
        except asyncio.TimeoutError:
            logger.debug(f"Timeout checking {ip}")
        except Exception as e:
            logger.debug(f"Failed to check {ip}: {e}")
        return None
    
    async def _check_port(self, ip: str, port: int, timeout: float = 2.0) -> bool:
        """Check if a port is open on the given IP"""
        try:
            future = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(future, timeout=timeout)
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False
    
    async def _get_device_info(self, session: aiohttp.ClientSession, ip: str, page_content: str = None) -> Optional[Dict]:
        """Extract device information from ESPHome device"""
        device_info = {
            "ip_address": ip,
            "ip": ip,  # Keep both for compatibility
            "is_online": True,
            "last_seen": timezone.now().isoformat()
        }
        
        try:
            # If we don't have page content, fetch it
            if not page_content:
                async with session.get(f"http://{ip}/", timeout=10) as response:
                    if response.status != 200:
                        return None
                    page_content = await response.text()
            
            # Extract basic info from main page
            self._parse_main_page(page_content, device_info)
            
            # Try to get more detailed info from /text_sensor endpoint
            try:
                async with session.get(f"http://{ip}/text_sensor", timeout=5) as response:
                    if response.status == 200:
                        text_sensors = await response.json()
                        self._parse_text_sensors(text_sensors, device_info)
            except:
                logger.debug(f"Could not fetch text sensors from {ip}")
            
            # Try to get sensor info
            try:
                async with session.get(f"http://{ip}/sensor", timeout=5) as response:
                    if response.status == 200:
                        sensors = await response.json()
                        device_info["sensors"] = self._parse_sensors(sensors)
            except:
                logger.debug(f"Could not fetch sensors from {ip}")
            
            # Try to get switch info
            try:
                async with session.get(f"http://{ip}/switch", timeout=5) as response:
                    if response.status == 200:
                        switches = await response.json()
                        if "sensors" not in device_info:
                            device_info["sensors"] = []
                        device_info["sensors"].extend(self._parse_switches(switches))
            except:
                logger.debug(f"Could not fetch switches from {ip}")
            
            # Try to get binary sensor info
            try:
                async with session.get(f"http://{ip}/binary_sensor", timeout=5) as response:
                    if response.status == 200:
                        binary_sensors = await response.json()
                        if "sensors" not in device_info:
                            device_info["sensors"] = []
                        device_info["sensors"].extend(self._parse_binary_sensors(binary_sensors))
            except:
                logger.debug(f"Could not fetch binary sensors from {ip}")
            
            # Generate MAC address if not found
            if "mac_address" not in device_info:
                device_info["mac_address"] = await self._generate_mac_from_device(session, ip, device_info)
            
            # Generate MQTT topic prefix if not found
            if "mqtt_topic_prefix" not in device_info and "name" in device_info:
                device_info["mqtt_topic_prefix"] = device_info["name"].lower().replace(" ", "_").replace("-", "_")
            
            # Ensure we have a name
            if "name" not in device_info:
                if "hostname" in device_info:
                    device_info["name"] = device_info["hostname"]
                else:
                    device_info["name"] = f"ESPHome_{ip.replace('.', '_')}"
            
            logger.info(f"Successfully discovered device: {device_info.get('name', ip)} at {ip}")
            return device_info
                        
        except Exception as e:
            logger.warning(f"Could not get complete device info from {ip}: {e}")
            # Return basic info even if detailed parsing fails
            if "name" not in device_info:
                device_info["name"] = f"ESPHome_{ip.replace('.', '_')}"
            if "mac_address" not in device_info:
                device_info["mac_address"] = f"esphome_{ip.replace('.', '')}"
            return device_info
    
    def _parse_main_page(self, content: str, device_info: dict):
        """Parse the main ESPHome web page for device information"""
        try:
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()
                if title and title != "ESPHome Web Server":
                    device_info["hostname"] = title
                    device_info["name"] = title
            
            # Look for device name in various formats
            name_patterns = [
                r'Device:\s*([^<\n\r]+)',
                r'<h1[^>]*>([^<]+)</h1>',
                r'<h2[^>]*>([^<]+)</h2>',
                r'device["\']?\s*:\s*["\']([^"\']+)["\']',
                r'name["\']?\s*:\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    if name and len(name) > 1:
                        device_info["name"] = name
                        break
            
            # Extract version
            version_patterns = [
                r'ESPHome\s+v?(\d+\.\d+\.\d+)',
                r'Version:\s*(\d+\.\d+\.\d+)',
                r'esphome["\']?\s*:\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in version_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    device_info["version"] = match.group(1)
                    break
            
            # Look for MAC address in page
            mac_patterns = [
                r'MAC:\s*([0-9A-Fa-f:]{17})',
                r'([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})',
                r'([0-9A-Fa-f]{12})'
            ]
            
            for pattern in mac_patterns:
                match = re.search(pattern, content)
                if match:
                    mac = match.group(1)
                    if len(mac) == 12:  # Format as MAC if it's 12 hex chars
                        mac = ':'.join([mac[i:i+2] for i in range(0, 12, 2)])
                    device_info["mac_address"] = mac.upper()
                    break
                    
        except Exception as e:
            logger.debug(f"Error parsing main page: {e}")
    
    def _parse_text_sensors(self, text_sensors: dict, device_info: dict):
        """Parse text sensor data for additional device info"""
        try:
            if isinstance(text_sensors, dict):
                for sensor_id, sensor_data in text_sensors.items():
                    if isinstance(sensor_data, dict):
                        value = sensor_data.get("value", "")
                        if "wifi" in sensor_id.lower() and "mac" in sensor_id.lower():
                            device_info["mac_address"] = value
                        elif "version" in sensor_id.lower():
                            device_info["version"] = value
                        elif "ip" in sensor_id.lower() and "address" in sensor_id.lower():
                            device_info["ip_address"] = value
        except Exception as e:
            logger.debug(f"Error parsing text sensors: {e}")
    
    def _parse_sensors(self, sensors: dict) -> List[Dict]:
        """Parse regular sensors"""
        parsed_sensors = []
        try:
            if isinstance(sensors, dict):
                for sensor_id, sensor_data in sensors.items():
                    if isinstance(sensor_data, dict):
                        sensor_info = {
                            "name": sensor_data.get("name", sensor_id),
                            "sensor_type": "sensor",
                            "last_value": sensor_data.get("value"),
                            "unit": sensor_data.get("unit_of_measurement", ""),
                            "device_class": self._get_device_class_from_id(sensor_id),
                            "is_controllable": False,
                            "topic": f"esphome/{sensor_id}/state"  # Approximate topic
                        }
                        parsed_sensors.append(sensor_info)
        except Exception as e:
            logger.debug(f"Error parsing sensors: {e}")
        return parsed_sensors
    
    def _parse_switches(self, switches: dict) -> List[Dict]:
        """Parse switch data"""
        parsed_switches = []
        try:
            if isinstance(switches, dict):
                for switch_id, switch_data in switches.items():
                    if isinstance(switch_data, dict):
                        switch_info = {
                            "name": switch_data.get("name", switch_id),
                            "sensor_type": "switch",
                            "last_value": switch_data.get("value"),
                            "device_class": "switch",
                            "is_controllable": True,
                            "topic": f"esphome/{switch_id}/state",
                            "command_topic": f"esphome/{switch_id}/command"
                        }
                        parsed_switches.append(switch_info)
        except Exception as e:
            logger.debug(f"Error parsing switches: {e}")
        return parsed_switches
    
    def _parse_binary_sensors(self, binary_sensors: dict) -> List[Dict]:
        """Parse binary sensor data"""
        parsed_binary = []
        try:
            if isinstance(binary_sensors, dict):
                for sensor_id, sensor_data in binary_sensors.items():
                    if isinstance(sensor_data, dict):
                        sensor_info = {
                            "name": sensor_data.get("name", sensor_id),
                            "sensor_type": "binary_sensor",
                            "last_value": sensor_data.get("value"),
                            "device_class": self._get_device_class_from_id(sensor_id),
                            "is_controllable": False,
                            "topic": f"esphome/{sensor_id}/state"
                        }
                        parsed_binary.append(sensor_info)
        except Exception as e:
            logger.debug(f"Error parsing binary sensors: {e}")
        return parsed_binary
    
    async def _generate_mac_from_device(self, session: aiohttp.ClientSession, ip: str, device_info: dict) -> str:
        """Generate a MAC address from device information"""
        try:
            # Try to get MAC from device info endpoint
            async with session.get(f"http://{ip}/info", timeout=3) as response:
                if response.status == 200:
                    info = await response.json()
                    if "mac_address" in info:
                        return info["mac_address"]
                    if "chip_id" in info:
                        chip_id = str(info["chip_id"])
                        if len(chip_id) >= 6:
                            # Generate MAC-like address from chip ID
                            mac_parts = []
                            for i in range(0, min(12, len(chip_id)), 2):
                                mac_parts.append(chip_id[i:i+2].zfill(2))
                            while len(mac_parts) < 6:
                                mac_parts.append("00")
                            return ":".join(mac_parts[:6]).upper()
        except:
            pass
        
        # Fallback: generate from IP and device name
        device_name = device_info.get("name", "unknown")
        ip_parts = ip.split(".")
        name_hash = str(hash(device_name))[-4:]
        
        mac = f"ESP:{ip_parts[-2].zfill(2)}:{ip_parts[-1].zfill(2)}:{name_hash[:2]}:{name_hash[2:4]}:00"
        return mac.upper()
    
    def _get_device_class_from_id(self, sensor_id: str) -> str:
        """Determine device class from sensor ID"""
        sensor_id_lower = sensor_id.lower()
        
        if "temperature" in sensor_id_lower or "temp" in sensor_id_lower:
            return "temperature"
        elif "humidity" in sensor_id_lower:
            return "humidity"
        elif "motion" in sensor_id_lower or "pir" in sensor_id_lower:
            return "motion"
        elif "door" in sensor_id_lower or "window" in sensor_id_lower:
            return "opening"
        elif "smoke" in sensor_id_lower:
            return "smoke"
        elif "gas" in sensor_id_lower:
            return "gas"
        elif "light" in sensor_id_lower or "lux" in sensor_id_lower:
            return "illuminance"
        elif "pressure" in sensor_id_lower:
            return "pressure"
        elif "voltage" in sensor_id_lower:
            return "voltage"
        elif "current" in sensor_id_lower:
            return "current"
        elif "power" in sensor_id_lower:
            return "power"
        elif "energy" in sensor_id_lower:
            return "energy"
        else:
            return ""
    
    def parse_esphome_log(self, log_content: str) -> Dict:
        """Parse ESPHome log content for device and sensor information"""
        device_info = {}
        sensors = []
        lines = log_content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Device information
            if "Local MAC:" in line or "WiFi MAC:" in line:
                mac_match = re.search(r'([0-9A-Fa-f:]{17})', line)
                if mac_match:
                    device_info["mac_address"] = mac_match.group(1).upper()
            elif "IP Address:" in line:
                ip_match = re.search(r'IP Address: (\d+\.\d+\.\d+\.\d+)', line)
                if ip_match:
                    device_info["ip_address"] = ip_match.group(1)
            elif "Hostname:" in line and "'" in line:
                hostname = re.search(r"'([^']+)'", line)
                if hostname:
                    device_info["hostname"] = hostname.group(1)
                    device_info["name"] = hostname.group(1)
            elif "ESPHome version" in line:
                version_match = re.search(r'ESPHome version (\d+\.\d+\.\d+)', line)
                if version_match:
                    device_info["version"] = version_match.group(1)
            elif "Signal strength:" in line:
                signal_match = re.search(r'Signal strength: (-?\d+) dB', line)
                if signal_match:
                    device_info["wifi_signal"] = int(signal_match.group(1))
            elif "Channel:" in line:
                channel_match = re.search(r'Channel: (\d+)', line)
                if channel_match:
                    device_info["wifi_channel"] = int(channel_match.group(1))
            elif "Topic Prefix:" in line and "'" in line:
                prefix_match = re.search(r"'([^']+)'", line)
                if prefix_match:
                    device_info["mqtt_topic_prefix"] = prefix_match.group(1)
            
            # Sensor information parsing
            elif any(sensor_type in line for sensor_type in ["MQTT Sensor", "MQTT Binary Sensor", "MQTT Switch", "MQTT Text Sensor", "MQTT Number"]):
                sensor_matches = re.findall(r"'([^']+)'", line)
                if sensor_matches:
                    sensor_name = sensor_matches[0]
                    
                    if "MQTT Sensor" in line:
                        sensor_type = "sensor"
                    elif "MQTT Binary Sensor" in line:
                        sensor_type = "binary_sensor"
                    elif "MQTT Switch" in line:
                        sensor_type = "switch"
                    elif "MQTT Text Sensor" in line:
                        sensor_type = "text_sensor"
                    elif "MQTT Number" in line:
                        sensor_type = "number"
                    else:
                        sensor_type = "sensor"
                    
                    sensor_info = {
                        "name": sensor_name,
                        "sensor_type": sensor_type,
                        "topic": "",
                        "command_topic": "",
                        "device_class": self._get_device_class_from_name(sensor_name),
                        "is_controllable": sensor_type in ["switch", "number"]
                    }
                    sensors.append(sensor_info)
                    
            elif "State Topic:" in line and "'" in line and sensors:
                topic_match = re.search(r"'([^']+)'", line)
                if topic_match:
                    sensors[-1]["topic"] = topic_match.group(1)
                    
            elif "Command Topic:" in line and "'" in line and sensors:
                topic_match = re.search(r"'([^']+)'", line)
                if topic_match:
                    sensors[-1]["command_topic"] = topic_match.group(1)
                    sensors[-1]["is_controllable"] = True
        
        return {"device": device_info, "sensors": sensors}
    
    def _get_device_class_from_name(self, sensor_name: str) -> str:
        """Get device class from sensor name"""
        return self._get_device_class_from_id(sensor_name)
    
    def save_discovered_device(self, device_data: Dict, sensors_data: List[Dict] = None) -> Tuple[ESPHomeDevice, bool]:
        """Save discovered device and sensors to database"""
        try:
            device_info = device_data.get("device", device_data)
            mac_address = device_info.get("mac_address")
            if not mac_address:
                logger.error("No MAC address found for device, skipping.")
                return None, False

            device_defaults = {
                "name": device_info.get("name", device_info.get("hostname", "Unknown Device")),
                "ip_address": device_info.get("ip_address", device_info.get("ip", "")),
                "hostname": device_info.get("hostname", ""),
                "version": device_info.get("version", ""),
                "is_online": device_info.get("is_online", True),
                "mqtt_topic_prefix": device_info.get("mqtt_topic_prefix", ""),
                "wifi_signal": device_info.get("wifi_signal"),
                "wifi_channel": device_info.get("wifi_channel"),
                "last_seen": timezone.now(),
            }

            device, created = ESPHomeDevice.objects.update_or_create(
                mac_address=mac_address,
                defaults=device_defaults
            )
            
            # Save sensors
            if not sensors_data:
                sensors_data = device_data.get("sensors", [])
            
            sensors_created = 0
            for sensor_data in sensors_data:
                if not sensor_data.get("name"):
                    continue
                    
                sensor_defaults = {
                    "topic": sensor_data.get("topic", ""),
                    "command_topic": sensor_data.get("command_topic", ""),
                    "unit": sensor_data.get("unit", ""),
                    "device_class": sensor_data.get("device_class", ""),
                    "icon": sensor_data.get("icon", ""),
                    "is_controllable": sensor_data.get("is_controllable", False),
                    "last_value": sensor_data.get("last_value", ""),
                    "last_updated": timezone.now(),
                }
                
                sensor, sensor_created = ESPHomeSensor.objects.update_or_create(
                    device=device,
                    name=sensor_data["name"],
                    sensor_type=sensor_data.get("sensor_type", "sensor"),
                    defaults=sensor_defaults
                )
                
                if sensor_created:
                    sensors_created += 1
            
            logger.info(f"{'Created' if created else 'Updated'} device: {device.name} "
                       f"with {len(sensors_data)} sensors ({sensors_created} new)")
            return device, created
            
        except Exception as e:
            logger.error(f"Error saving discovered device: {e}")
            logger.exception("Full traceback:")
            return None, False
    
    async def discover_and_save_devices(self, network_range: str = "192.168.0.0/24") -> List[ESPHomeDevice]:
        """Discover devices and save them to database"""
        discovered_devices = await self.discover_devices_by_network_scan(network_range)
        saved_devices = []
        
        for device_data in discovered_devices:
            try:
                device, created = self.save_discovered_device(device_data)
                if device:
                    saved_devices.append(device)
            except Exception as e:
                logger.error(f"Error saving device {device_data.get('name', 'unknown')}: {e}")
        
        logger.info(f"Successfully saved {len(saved_devices)} devices to database")
        return saved_devices