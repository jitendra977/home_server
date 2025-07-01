from django.db import models
import json

class ESPHomeDevice(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17, unique=True)
    hostname = models.CharField(max_length=100)
    version = models.CharField(max_length=20, blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=False)
    mqtt_topic_prefix = models.CharField(max_length=100, blank=True)
    wifi_signal = models.IntegerField(null=True, blank=True)
    wifi_channel = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.ip_address})"
    
    @property
    def signal_strength_display(self):
        if self.wifi_signal is None:
            return "Unknown"
        
        if self.wifi_signal >= -30:
            return "Excellent ▂▄▆█"
        elif self.wifi_signal >= -50:
            return "Good ▂▄▆"
        elif self.wifi_signal >= -70:
            return "Fair ▂▄"
        else:
            return "Poor ▂"

class ESPHomeSensor(models.Model):
    SENSOR_TYPES = [
        ('temperature', 'Temperature'),
        ('humidity', 'Humidity'),
        ('motion', 'Motion'),
        ('binary', 'Binary Sensor'),
        ('switch', 'Switch'),
        ('number', 'Number'),
        ('text', 'Text Sensor'),
        ('light', 'Light'),
        ('fan', 'Fan'),
        ('cover', 'Cover'),
        ('climate', 'Climate'),
    ]
    
    device = models.ForeignKey(ESPHomeDevice, on_delete=models.CASCADE, related_name='sensors')
    name = models.CharField(max_length=100)
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPES)
    topic = models.CharField(max_length=200)
    command_topic = models.CharField(max_length=200, blank=True)
    unit = models.CharField(max_length=10, blank=True)
    device_class = models.CharField(max_length=50, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    last_value = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_controllable = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['device', 'name', 'sensor_type']
        ordering = ['device__name', 'sensor_type', 'name']
    
    def __str__(self):
        return f"{self.device.name} - {self.name} ({self.sensor_type})"
    
    @property
    def formatted_value(self):
        if not self.last_value:
            return "No data"
        
        value = self.last_value
        if self.unit:
            return f"{value} {self.unit}"
        return value