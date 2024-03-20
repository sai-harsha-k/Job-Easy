from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    resume_text = models.TextField(blank=True, null=True)  # Field to store extracted resume text

    def __str__(self):
        return self.user.username
