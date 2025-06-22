from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField(max_length=100)
    floor = models.CharField(max_length=50, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)
    image = models.ImageField(upload_to='appliances/room_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # ADD THIS LINE ✅

    def __str__(self):
        return f"{self.name} ({self.floor})" if self.floor else self.name


class Appliance(models.Model):
    DEVICE_TYPES = [
        ('light', 'Light'),
        ('fan', 'Fan'),
        ('ac', 'Air Conditioner'),
        ('tv', 'Television'),
        ('socket', 'Smart Socket'),
        ('sensor', 'Sensor'),
    ]

    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=30, choices=DEVICE_TYPES, default='light')
    location = models.CharField(max_length=100, help_text="Example: Top wall, under table")
    status = models.BooleanField(default=False, help_text="True = ON, False = OFF")
    is_active = models.BooleanField(default=True, help_text="True = available in system")
    
    room = models.ForeignKey(Room, related_name='appliances', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appliances', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def toggle_status(self):
        self.status = not self.status
        self.save()

    def __str__(self):
        return f"{self.name} ({self.device_type})"