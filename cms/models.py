from django.db import models

# Create your models here.
class CinemaInfo(models.Model):
    name = models.CharField(max_length=100, default="Mi Cine")
    address = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)


    def __str__(self):
        return self.name