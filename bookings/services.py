from django.core.exceptions import ValidationError
from .models import Ticket, Seat, Booking
from movies.models import Function
from users.models import CustomUser
from django.core.mail import EmailMessage
from django.conf import settings
import qrcode
import os


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
        if not seat_ids:
            return Response({'message': 'No se enviaron asientos'}, status=statu
"""

"""
Evitar reservas de asientos que ya están ocupados
"""

def check_seat_availability(seat, function):
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


def check_capacity(booking, function, hall):
    """
    Cuenta los asientos reservados para una determinada funcion
    :param booking: reserva de asientos
    :param function: funcion de la cual se quiere evaluar la disponibilidad
    :param hall: sala asociada a la funcion
    """

    # parametros de prueba, cuando tenga salas cargadas en la base de datos se cambia por consultas en tiempo real
    hall1_capacity = 150
    hall2_capacity = 175

    total_booked_seats = Tickets.objects.filter()


def release_expired_reservations():
    """
    Libera los asientos reservados si el pago no se completó en el tiempo establecido
    """
    from bookings.models import Booking

    # Filtrar las reservas pendientes que hayan expirado
    expired_bookings = Booking.object.filter(status='pending').filter(
        reserved_at__lt=timezone.now() - timedelta(minutes=15)
    )

    for booking in expired_bookings:
        booking.status = 'cancelled'
        booking.save()


def generate_qr_code(ticket):
    """
    Genera un código QR para el ticket con información esencial
    """
    qr_data = f'Ticket ID: {ticket.id}, Código: {ticket.ticket_code}, Función: {ticket.booking.function}'
    qr = qrcode.make(qr_data)

    qr_path = f"f{settomgs.MEDIA_ROOT}/qr_codes/ticket_{ticket.id}.png"
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    qr.save(qr_path)

    return qr_path


def send_confirmation_email(ticket, qr_code_path):
    """
    Envía un correo de confirmación al usuario con el QR adjunto
    """
    subject = "Confirmación de compra - CineApp"
    message = (f'Hola {ticket.booking.user.username},\n\nTu compra ha sido confirmada para la función "'
               f'{ticket.booking.function.movie.title}". Adjuntamos tu código QR para el ingreso.\n\n¡Gracias por elegirnos!')
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [ticket.booking.user,email])

    # Adjuntar el codigo qr
    if os.path.exists(qr_code_path):
        email.attach_file(qr_code_path)

    email.send()