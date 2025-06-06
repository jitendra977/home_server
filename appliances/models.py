#appliances/models.py
from django.db import models

class Appliance(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({'ON' if self.status else 'OFF'})"
    
class Members(models.Model):
    name = models.CharField()
    phone = models.CharField()
    email = models.EmailField(default=None)