from django.db import models
from django.db.models import CASCADE

from movies.models import Hall
from users.models import CustomUser
from movies.models import Function

# Create your models here.
class Seat(models.Model):

    """
    Asientos que el usuario reservera en la compra de su entrada
    """
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    row = models.CharField(max_length=5)
    number = models.IntegerField()
    seat_available = models.BooleanField(default=True) # Si el asiento esta disponible se puede seleccionar en la compra


class Booking(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=CASCADE)
    function = models.ForeignKey(Function, on_delete=CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2 ,blank=True)  # El precio tiene que calcularse
    created_at = models.DateTimeField(auto_now_add=True)                            # dependiendo de el precio de la
    status = models.CharField(                                                      # función y la cantidad de tickets
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('paid', 'Pagado'),
            ('cancelled', 'cancelado'),
            ('expired', 'Expirado')
        ]
    )

class Ticket(models.Model):

    """
    Ticket o entrada del cliente
    """
    booking = models.ForeignKey(Booking, on_delete=CASCADE, related_name='tickets')
    seat = models.ForeignKey(Seat, on_delete=CASCADE)
    ticket_code = models.CharField(max_length=100, unique=True) # Codigo unico para generar codigo QR
    issued_at = models.DateTimeField(auto_now_add=True)
    is_scanned = models.BooleanField(default=False)

