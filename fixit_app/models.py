from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

def validate_year(value):
    if value < 1900 or value > 2025:
        raise ValidationError('Year of birth must be between 1900 and 2025.')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    year_of_birth = models.PositiveIntegerField(null=True, blank=True, validators=[validate_year])

    def __str__(self):
        return self.user.username
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    question = models.TextField()
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} asked: {self.question[:50]}"