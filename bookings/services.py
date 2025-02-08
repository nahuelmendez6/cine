from django.core.exceptions import ValidationError
from .models import Ticket, Seat, Booking
from movies.models import Function
from users.models import CustomUser



MAX_TICKETS_PER_USER = 10


def generate_ticket_code(user, seat, function):
    """
    Genera un codigo único para cada ticker
    """
    import uuid
    return f"{user.id}-{function.id}-{seat.id}-{uuid.uuid4().hex[:6]}"

"""
DEberia agregar una funcion que revise la disponibilidad de asientos
es decir, si la funcion ya esta agotada o no

"""



"""
Evitar reservas de asientos que ya están ocupados
"""

def reserve_seat(user, seat, function):
    """
    Verifica si un asiento esta disponible o reservado para
    una función en específico
    """
    price_per_ticket = function.price  # Asegúrate de que `function` tenga el atributo `price`

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
        defaults={'status':'pending', 'total_price': price_per_ticket},
    )

    """
    Crear el ticker asociado al asiento
    """
    ticket = Ticket.objects.create(
        booking=booking,
        seat=seat,
        ticket_code=generate_ticket_code(user, seat, function)
    )

    """ Marcar el asiento como no disponible  """
    seat.seat_available = False
    seat.save()

    return ticket


def validate_ticket_purchase(user, tickets_requested, function):
    """
    Valida y procesa la compra de entradas por un usuario para una función específica

    :param user: El usuario que está realizando la compra.
    :param function: La función para la cual se están comprando las entradas.
    :param seats_requested: Lista de asientos seleccionados para la compra
    :return: Lista de asientos reservados
    """

    # Contar cuantos tickets ya tiene el usuario para esa funcion
    existing_tickets = Ticket.objects.filter(booking__user=user, booking__function=function).count()

    # Contar cuantos asientos se han seleccionado
    amount_ticket_requested = len(tickets_requested)

    # Validar el límite de tickets
    if existing_tickets + amount_ticket_requested > MAX_TICKETS_PER_USER:
        return ValidationError(f"No puedes comprar más de {MAX_TICKETS_PER_USER} para una misma función")

    # Reservar cada asiento
    tickets = []
    for seat in tickets_requested:
        ticket = reserve_seat(user, seat, function)
        tickets.append(ticket)

    return tickets
