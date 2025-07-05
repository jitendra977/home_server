# from django.apps import AppConfig
# import threading
# import logging

# class ControlConfig(AppConfig):
#     name = 'control'
#     started_mqtt = False

#     def ready(self):
#         if not self.started_mqtt:
#             try:
#                 from .services.mqtt_client import ESPHomeMQTTClient
#                 mqtt_client = ESPHomeMQTTClient()
#                 thread = threading.Thread(target=mqtt_client.connect_and_loop, daemon=True)
#                 thread.start()
#                 self.started_mqtt = True
#             except Exception as e:
#                 logging.getLogger(__name__).error(f"MQTT listener failed to start: {e}")