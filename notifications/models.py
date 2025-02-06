from django.db import models

from users.models import CustomUser


# Create your models here.
class Notification(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)