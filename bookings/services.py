from django.core.exceptions import ValidationError
from .models import Ticket
from users.models import CustomUser

"""
Evitar reservas de asientos que ya están ocupados
"""

def reserve_seat(user, seat):
    if Ticket.objects.filter(seat=seat):
        pass