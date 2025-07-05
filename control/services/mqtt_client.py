from django.http import JsonResponse
import paho.mqtt.client as mqtt
import json
import logging
from django.conf import settings
from django.utils import timezone
from ..models import ESPHomeDevice, ESPHomeSensor
import threading
import re
import time

# Set up more detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ESPHomeMQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe
        
        self.broker_host = getattr(settings, 'MQTT_BROKER_HOST', '192.168.0.59')
        self.broker_port = getattr(settings, 'MQTT_BROKER_PORT', 1883)
        self.username = getattr(settings, 'MQTT_USERNAME', None)
        self.password = getattr(settings, 'MQTT_PASSWORD', None)
        
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        self.connected = False
        self.subscribed_topics = set()
        self.message_count = 0
        
    def on_subscribe(self, client, userdata, mid, granted_qos):
        logger.info(f"Successfully subscribed to topic (mid: {mid}, QoS: {granted_qos})")
        
    def on_unsubscribe(self, client, userdata, mid):
        logger.info(f"Unsubscribed from topic (mid: {mid})")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info(f"✅ Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            logger.info(f"Connection flags: {flags}")
            
            # Subscribe to ALL topics for debugging (remove in production)
            logger.info("🔍 Subscribing to ALL topics for debugging...")
            client.subscribe("#")
            self.subscribed_topics.add("#")
            
            # Subscribe to Home Assistant discovery messages
            client.subscribe("homeassistant/+/+/+/config")
            client.subscribe("homeassistant/+/+/config")  # Some devices use shorter format
            self.subscribed_topics.add("homeassistant/+/+/+/config")
            self.subscribed_topics.add("homeassistant/+/+/config")
            logger.info("📡 Subscribed to Home Assistant discovery topics")
            
            # Subscribe to ESPHome status topics
            client.subscribe("+/status")
            self.subscribed_topics.add("+/status")
            
            # Subscribe to common ESPHome patterns
            common_patterns = [
                "+/sensor/+/state",
                "+/binary_sensor/+/state", 
                "+/switch/+/state",
                "+/number/+/state",
                "+/text_sensor/+/state",
                "+/light/+/state",
                "+/fan/+/state",
                "+/cover/+/state",
                "+/climate/+/state",
                "esphome/+/state",
                "tasmota/+/STATE",
                "zigbee2mqtt/+",
            ]
            
            for pattern in common_patterns:
                client.subscribe(pattern)
                self.subscribed_topics.add(pattern)
                logger.debug(f"📡 Subscribed to pattern: {pattern}")
            
            # Try to get existing devices and subscribe to their topics
            try:
                devices = ESPHomeDevice.objects.all()
                logger.info(f"📱 Found {devices.count()} existing devices in database")
                
                for device in devices:
                    logger.info(f"Device: {device.name}, Topic prefix: {device.mqtt_topic_prefix}")
                    if device.mqtt_topic_prefix:
                        topics = [
                            f"{device.mqtt_topic_prefix}/+/+/state",
                            f"{device.mqtt_topic_prefix}/+/state", 
                            f"{device.mqtt_topic_prefix}/status",
                            f"{device.mqtt_topic_prefix}/#",  # All subtopics
                        ]
                        
                        for topic in topics:
                            client.subscribe(topic)
                            self.subscribed_topics.add(topic)
                            logger.debug(f"📡 Subscribed to device topic: {topic}")
                            
            except Exception as e:
                logger.error(f"❌ Error subscribing to device topics: {e}")
                
            # Request discovery after a short delay
            def request_discovery_delayed():
                time.sleep(2)
                self.request_discovery()
                
            discovery_thread = threading.Thread(target=request_discovery_delayed)
            discovery_thread.start()
            
        else:
            error_codes = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier", 
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorised"
            }
            logger.error(f"❌ Failed to connect to MQTT broker: {error_codes.get(rc, f'Unknown error {rc}')}")
    
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        logger.warning(f"⚠️ Disconnected from MQTT broker: {rc}")
        if rc != 0:
            logger.warning("Unexpected disconnection. Will attempt to reconnect.")
    
    def on_log(self, client, userdata, level, buf):
        log_levels = {
            mqtt.MQTT_LOG_DEBUG: logger.debug,
            mqtt.MQTT_LOG_INFO: logger.info,
            mqtt.MQTT_LOG_NOTICE: logger.info,
            mqtt.MQTT_LOG_WARNING: logger.warning,
            mqtt.MQTT_LOG_ERR: logger.error
        }
        log_func = log_levels.get(level, logger.info)
        log_func(f"MQTT: {buf}")
    
    def on_message(self, client, userdata, msg):
        self.message_count += 1
        topic = msg.topic
        try:
            payload = msg.payload.decode('utf-8')
        except UnicodeDecodeError:
            payload = msg.payload.hex()
            logger.warning(f"Non-UTF8 payload received on {topic}: {payload}")
            return
            
        logger.info(f"📨 Message #{self.message_count} - Topic: {topic}")
        logger.info(f"    Payload: {payload[:200]}{'...' if len(payload) > 200 else ''}")

        try:
            # Handle Home Assistant MQTT discovery messages
            if topic.startswith("homeassistant/") and topic.endswith("/config"):
                logger.info(f"🔍 Processing Home Assistant discovery message")
                self.parse_homeassistant_discovery(topic, payload)
                
            # Handle status messages
            elif topic.endswith("/status") or topic.endswith("/STATUS"):
                logger.info(f"📊 Processing status message")
                self.handle_availability_message(topic, payload)
                
            # Handle state updates
            elif "/state" in topic.lower() or topic.endswith("/STATE"):
                logger.info(f"🔄 Processing state update")
                self.handle_state_update(topic, payload)
                
            # Handle other common patterns
            elif any(pattern in topic.lower() for pattern in ['sensor', 'switch', 'light', 'binary']):
                logger.info(f"🔄 Processing sensor/device message")
                self.handle_state_update(topic, payload)
                
            else:
                logger.debug(f"📝 Unhandled topic pattern: {topic}")
                
        except Exception as e:
            logger.error(f"❌ Error processing message on topic {topic}: {e}")
            logger.exception("Full traceback:")

    def parse_homeassistant_discovery(self, topic, payload):
        """Enhanced discovery parsing with better error handling"""
        try:
            if not payload or payload.strip() == "":
                logger.warning(f"Empty payload for discovery topic: {topic}")
                return
                
            logger.info(f"🔍 Parsing discovery for topic: {topic}")
            data = json.loads(payload)
            logger.debug(f"Discovery data keys: {list(data.keys())}")
            
            # Log the full discovery message for debugging
            logger.debug(f"Full discovery data: {json.dumps(data, indent=2)}")
            
            device_info = data.get('device') or data.get('dev', {})
            if not device_info:
                logger.warning(f"No device info in discovery message for {topic}")
                return

            # Extract device information
            identifiers = device_info.get('identifiers') or device_info.get('ids', [])
            if isinstance(identifiers, list) and identifiers:
                identifier = identifiers[0]
            else:
                identifier = identifiers
                
            device_name = device_info.get('name', str(identifier))
            
            # Better topic prefix extraction
            topic_prefix = self.extract_topic_prefix(topic, data, device_info)
            
            logger.info(f"Device: {device_name}, Prefix: {topic_prefix}, Identifier: {identifier}")

            # MAC address extraction
            mac_address = self.extract_mac_address(device_info, identifier)
            
            # Other device info
            ip_address = device_info.get('ip_address', '0.0.0.0')
            hostname = device_info.get('name', topic_prefix)
            version = device_info.get('sw', device_info.get('sw_version', ''))

            # Normalize MAC
            if mac_address:
                mac_address = mac_address.lower().replace(':', '').replace('-', '')
            else:
                logger.warning("No MAC address found in MQTT discovery, skipping device.")
                return

            # Get existing device if any
            existing = ESPHomeDevice.objects.filter(mac_address=mac_address).first()
            if not ip_address or ip_address == "0.0.0.0":
                if existing and existing.ip_address and existing.ip_address != "0.0.0.0":
                    ip_address = existing.ip_address

            device, created = ESPHomeDevice.objects.update_or_create(
                mac_address=mac_address,
                defaults={
                    'name': device_name or topic_prefix,
                    'ip_address': ip_address,
                    'hostname': hostname,
                    'version': version,
                    'is_online': True,
                    'mqtt_topic_prefix': topic_prefix,
                    'last_seen': timezone.now(),
                }
            )
            
            action = "Created" if created else "Updated"
            logger.info(f"✅ {action} device: {device.name}")
            
            if not created:
                device.is_online = True
                device.last_seen = timezone.now()
                if topic_prefix and device.mqtt_topic_prefix != topic_prefix:
                    device.mqtt_topic_prefix = topic_prefix
                device.save(update_fields=['is_online', 'last_seen', 'mqtt_topic_prefix'])

            # Parse entity/sensor information
            self.parse_entity_info(topic, data, device)

        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in discovery message for {topic}: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to parse discovery for {topic}: {e}")
            logger.exception("Full traceback:")
    
    def extract_topic_prefix(self, topic, data, device_info):
        """Extract topic prefix from various sources"""
        # Try to get from topic structure
        parts = topic.split('/')
        if len(parts) >= 3:
            # homeassistant/sensor/device_name_entity/config
            entity_id = parts[2]
            # Extract device part (everything before last underscore typically)
            if '_' in entity_id:
                potential_prefix = '_'.join(entity_id.split('_')[:-1])
                if potential_prefix:
                    return potential_prefix
        
        # Try to get from data
        state_topic = data.get('stat_t') or data.get('state_topic', '')
        if state_topic:
            # Extract first part of state topic
            topic_parts = state_topic.split('/')
            if topic_parts:
                return topic_parts[0]
        
        # Fallback to device name
        device_name = device_info.get('name', '')
        if device_name:
            return device_name.lower().replace(' ', '_').replace('-', '_')
        
        return 'unknown'
    
    def extract_mac_address(self, device_info, identifier):
        """Extract MAC address from device info"""
        # Check connections
        if 'cns' in device_info:
            for conn in device_info['cns']:
                if conn[0] == 'mac':
                    return conn[1]
        
        # Try to format identifier as MAC if it looks like one
        if identifier and isinstance(identifier, str) and len(identifier) == 12:
            try:
                return ':'.join([identifier[i:i+2] for i in range(0, 12, 2)])
            except:
                pass
        
        return None
    
    def parse_entity_info(self, topic, data, device):
        """Parse entity/sensor information from discovery data"""
        logger.debug(f"[ENTITY DEBUG] topic: {topic}")
        logger.debug(f"[ENTITY DEBUG] data: {json.dumps(data, indent=2)}")
        try:
            parts = topic.split('/')
            if len(parts) < 3:
                return

            sensor_type = parts[1]  # sensor, binary_sensor, switch, etc.
            object_id = parts[2]
            sensor_name = data.get('name', object_id.replace('_', ' ').title())

            logger.info(f"Parsing entity: {sensor_name} (type: {sensor_type})")

            # Map sensor types to your model's choices
            type_map = {
                'sensor': self.guess_sensor_type(object_id, data),
                'binary_sensor': 'binary',
                'switch': 'switch',
                'number': 'number',
                'text_sensor': 'text',
                'light': 'light',
                'fan': 'fan',
                'cover': 'cover',
                'climate': 'climate',
                'button': 'button',
                'select': 'select',
            }
            mapped_type = type_map.get(sensor_type, 'binary')

            # Extract topics and properties
            state_topic = data.get('stat_t') or data.get('state_topic', '')
            command_topic = data.get('cmd_t') or data.get('command_topic', '')
            unit = data.get('unit_of_meas', '') or data.get('unit_of_measurement', '') or data.get('unit', '')
            device_class = data.get('dev_cla', '') or data.get('device_class', '')
            icon = data.get('icon', '')
            is_controllable = sensor_type in ['switch', 'number', 'light', 'fan', 'cover', 'climate', 'button', 'select']

            # Get or create sensor
            sensor, created = ESPHomeSensor.objects.get_or_create(
                device=device,
                name=sensor_name,
                sensor_type=mapped_type,
                defaults={
                    'topic': state_topic,
                    'command_topic': command_topic,
                    'unit': unit,
                    'device_class': device_class,
                    'icon': icon,
                    'is_controllable': is_controllable,
                    'last_updated': timezone.now(),
                }
            )

            action = "Created" if created else "Updated"
            logger.info(f"✅ {action} sensor: {device.name} - {sensor_name}")

            # Update existing sensor if needed
            updated_fields = []
            if not created:
                if sensor.topic != state_topic:
                    sensor.topic = state_topic
                    updated_fields.append('topic')
                if sensor.command_topic != command_topic:
                    sensor.command_topic = command_topic
                    updated_fields.append('command_topic')
                if sensor.sensor_type != mapped_type:
                    sensor.sensor_type = mapped_type
                    updated_fields.append('sensor_type')
                if updated_fields:
                    sensor.save(update_fields=updated_fields)
                    logger.info(f"Updated sensor fields: {updated_fields}")

        except Exception as e:
            logger.error(f"❌ Error parsing entity info: {e}")
    
    def guess_sensor_type(self, object_id, data):
        """Guess sensor type from object_id and data"""
        object_id_lower = object_id.lower()
        unit = (data.get('unit_of_meas', '') or data.get('unit_of_measurement', '')).lower()
        device_class = (data.get('dev_cla', '') or data.get('device_class', '')).lower()
        
        if 'temp' in object_id_lower or device_class == 'temperature' or '°c' in unit or '°f' in unit:
            return 'temperature'
        elif 'humid' in object_id_lower or device_class == 'humidity' or '%' in unit:
            return 'humidity'
        elif 'pressure' in object_id_lower or device_class == 'pressure':
            return 'pressure'
        elif 'voltage' in object_id_lower or 'v' == unit:
            return 'voltage'
        elif 'current' in object_id_lower or 'a' == unit:
            return 'current'
        elif 'power' in object_id_lower or 'w' == unit:
            return 'power'
        elif 'energy' in object_id_lower or 'kwh' in unit:
            return 'energy'
        else:
            return 'binary'
    
    def handle_availability_message(self, topic, payload):
        """Handle device availability/status messages"""
        logger.info(f"📊 Availability update: {topic} -> {payload}")
        
        # Extract topic prefix (device name)
        topic_prefix = topic.split('/')[0]
        
        try:
            device = ESPHomeDevice.objects.filter(mqtt_topic_prefix=topic_prefix).first()
            if device:
                is_online = payload.lower() in ['online', 'on', '1', 'true']
                device.is_online = is_online
                device.last_seen = timezone.now()
                device.save(update_fields=['is_online', 'last_seen'])
                logger.info(f"✅ Updated {device.name} online status: {is_online}")
            else:
                logger.warning(f"⚠️ No device found for topic prefix: {topic_prefix}")
        except Exception as e:
            logger.error(f"❌ Error updating device availability: {e}")
    
    def handle_state_update(self, topic, payload):
        """Enhanced state update handling"""
        try:
            logger.debug(f"Processing state update for topic: {topic}")
            
            # Try to find sensor by exact topic match first
            sensor = ESPHomeSensor.objects.filter(topic=topic).first()
            
            if not sensor:
                # Try pattern matching
                sensor = self.find_sensor_by_topic_pattern(topic)
            
            if sensor:
                old_value = sensor.last_value
                sensor.last_value = payload
                sensor.last_updated = timezone.now()
                sensor.save(update_fields=['last_value', 'last_updated'])
                
                logger.info(f"✅ Updated {sensor.device.name} - {sensor.name}: {old_value} -> {payload}")
                
                # Update device status
                sensor.device.last_seen = timezone.now()
                sensor.device.is_online = True
                sensor.device.save(update_fields=['last_seen', 'is_online'])
            else:
                logger.warning(f"⚠️ No sensor found for state topic: {topic}")
                # Log available sensors for debugging
                self.log_available_sensors()
                
        except Exception as e:
            logger.error(f"❌ Error handling state update for topic {topic}: {e}")
    
    def find_sensor_by_topic_pattern(self, topic):
        """Find sensor using various topic patterns"""
        topic_parts = topic.split('/')
        
        if len(topic_parts) >= 2:
            device_prefix = topic_parts[0]
            
            try:
                device = ESPHomeDevice.objects.filter(mqtt_topic_prefix=device_prefix).first()
                if device:
                    # Try different patterns to match sensor
                    sensors = ESPHomeSensor.objects.filter(device=device)
                    
                    # Try exact topic match in case of case sensitivity
                    for sensor in sensors:
                        if sensor.topic.lower() == topic.lower():
                            return sensor
                    
                    # Try partial matches
                    if len(topic_parts) >= 3:
                        sensor_part = topic_parts[2] if len(topic_parts) > 2 else topic_parts[1]
                        sensor_name = sensor_part.replace('_', ' ')
                        
                        for sensor in sensors:
                            if sensor_name.lower() in sensor.name.lower() or sensor.name.lower() in sensor_name.lower():
                                return sensor
                
            except Exception as e:
                logger.error(f"Error in pattern matching: {e}")
        
        return None
    
    def log_available_sensors(self):
        """Log available sensors for debugging"""
        try:
            sensors = ESPHomeSensor.objects.select_related('device').all()[:10]  # Limit to avoid spam
            logger.debug(f"Available sensors (showing first 10):")
            for sensor in sensors:
                logger.debug(f"  - {sensor.device.name}: {sensor.name} (topic: {sensor.topic})")
        except Exception as e:
            logger.error(f"Error logging available sensors: {e}")
    
    def request_discovery(self):
        """Request devices to send discovery messages"""
        try:
            logger.info("🔍 Requesting device discovery...")
            
            # Multiple discovery request methods
            discovery_requests = [
                ("homeassistant/status", "online"),
                ("homeassistant/discovery", "refresh"),
                ("cmnd/tasmotas/SetOption19", "1"),  # Tasmota discovery
            ]
            
            for topic, payload in discovery_requests:
                result = self.client.publish(topic, payload)
                logger.info(f"Discovery request sent to {topic}: {payload} (result: {result.rc})")
                
        except Exception as e:
            logger.error(f"❌ Error requesting discovery: {e}")
    
    def get_debug_info(self):
        """Get comprehensive debug information"""
        return {
            'connected': self.connected,
            'broker': f"{self.broker_host}:{self.broker_port}",
            'username': self.username,
            'subscribed_topics': list(self.subscribed_topics),
            'message_count': self.message_count,
            'devices_in_db': ESPHomeDevice.objects.count(),
            'sensors_in_db': ESPHomeSensor.objects.count(),
        }
    
    # ... rest of the methods remain the same ...
    
    def connect_and_loop(self):
        try:
            logger.info(f"🔌 Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_forever()
        except Exception as e:
            logger.error(f"❌ Error connecting to MQTT broker: {e}")
    
    def disconnect(self):
        if self.connected:
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")
    
    def publish_command(self, topic_prefix, sensor_name, command):
        """
        Publish a command to the MQTT topic for a given device/sensor.
        """
        # Find the sensor object
        try:
            sensor = ESPHomeSensor.objects.filter(
                device__mqtt_topic_prefix=topic_prefix,
                name=sensor_name
            ).first()
            if not sensor or not sensor.command_topic:
                logger.error(f"No command topic found for {topic_prefix} {sensor_name}")
                return False

            # Publish the command
            result = self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
            self.client.loop_start()
            info = self.client.publish(sensor.command_topic, command)
            info.wait_for_publish()
            self.client.loop_stop()
            self.client.disconnect()
            logger.info(f"Published '{command}' to {sensor.command_topic}")
            return True
        except Exception as e:
            logger.error(f"Error publishing command: {e}")
            return False

# Add this debug view to test the MQTT client
def debug_mqtt_view(request):
    """Debug view to check MQTT status"""
    if not hasattr(request, '_mqtt_client'):
        request._mqtt_client = ESPHomeMQTTClient()
        
    debug_info = request._mqtt_client.get_debug_info()
    
    return JsonResponse({
        'status': 'ok',
        'debug_info': debug_info,
        'devices': list(ESPHomeDevice.objects.values('name', 'mqtt_topic_prefix', 'is_online', 'last_seen')),
        'sensors': list(ESPHomeSensor.objects.select_related('device').values(
            'device__name', 'name', 'topic', 'last_value', 'last_updated'
        )[:20])  # Limit to avoid large responses
    })