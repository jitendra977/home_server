from django.db import models
from django.contrib.auth.models import User

def user_image_upload_path(instance, filename):
    return f'user_profiles/{instance.user.username}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_image_upload_path, blank=True, null=True)
    
    def __str__(self):
        return self.user.username