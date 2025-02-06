from django.core.exceptions import ValidationError
from .models import Ticket, Seat, Booking
from movies.models import Function
from users.models import CustomUser


"""
Evitar reservas de asientos que ya están ocupados
"""

def reserve_seat(user, seat, function):
    """
    Verifica si un asiento esta disponible o reservado para
    una función en específico
    """
    if Ticket.objects.filter(seat=seat, booking__function=function, booking__status=['pending', 'paid']).exists():
        """
        Esta condición verifica que el asiento esté asociado a una reservación (booking) y  una función, también verifica
        si se har realizado el pago del mismo
        """
        raise ValidationError("Este asiento ya está reservado para esta función")

    """
    Verificar que el asiento esté marcado como disponible
    """
    if not seat.seat_available:
        raise ValidationError("Este asiento no está disponible")


    """
    Crear o reuperar reserva del usuario para la funcion
    """
    booking, created = Booking.objects.get_or_create(
        user=user,
        function=function,
        defaults={'status':'pending'}
    )

    """
    Crear el ticker asociado al asiento
    """
    ticket = Ticket.object.create(
        booking=booking,
        seat=seat,
        ticket_code=generate_ticket_code(user, seat, function)
    )

    """ Marcar el asiento como no disponible  """
    seat.seat_available = False
    seat.save()

    return ticket

def generate_ticket_code(user, seat, function):
    """
    Genera un codigo único para cada ticker
    """
    import uuid
    return f"{user.id}-{function.id}-{seat-id}-{uuid.uuid4().hex[:6]}"