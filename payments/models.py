from django.db import models
import uuid

from bookings.models import Booking


# Create your models here.
class Payment(models.Model):

    bookig = models.OneToOneField(Booking, on_delete=models.CASCADE)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pendiente'), ('completed', 'Completado')])
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)


class Promotion(models.Model):

    promotion_name = models.CharField(max_length=255)
    promotion_description = models.TextField()
    discount_type = models.CharField(max_length=50, choices=[
        ('percentage', 'Porcentaje'),
        ('fixed', 'Monto fijo'),
        ('2x1', '2x1')
    ])
    discount_value = models.DecimalField(max_digits=5, decimal_places=2)   # Ej: 10 para 10%
    applicable_day = models.CharField(max_length=20, null=True, blank=True)
    min_tickets = models.ImageField(null=True, blank=True)
    card_type = models.CharField(max_length=20, null=True, blank=True)  # Ej: debit, credit
    days_before_function = models.ImageField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name