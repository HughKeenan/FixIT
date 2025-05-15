from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    year_of_birth = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.user.username
    