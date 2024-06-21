from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.

class Following(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed")

    class Meta:
	    unique_together = ('follower', 'followed') 

