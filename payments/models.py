from django.db import models
import uuid

from bookings.models import Booking


# Create your models here.
class Payment(models.Model):

    bookig = models.OneToOneField(Booking, on_delete=models.CASCADE)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pendiente'), ('completed', 'Completado')])
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)