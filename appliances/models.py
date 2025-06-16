#appliances/models.py
from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Appliance(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    room = models.ForeignKey(Room, related_name='appliances', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices', null=True, blank=True)

    def __str__(self):
        return self.name
    
class Members(models.Model):
    name = models.CharField()
    phone = models.CharField()
    email = models.EmailField(default=None)

