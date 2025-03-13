from django.core.exceptions import ValidationError
from .models import Ticket, Seat, Booking
from movies.models import Function
from users.models import CustomUser
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import qrcode
import os
import logging

logger = logging.getLogger(__name__)

MAX_TICKETS_PER_USER = 10
RESERVATION_EXPIRY_MINUTES = 15


def generate_ticket_code(user, seat, function):
    """
    Genera un código único para cada ticket
    
    Args:
        user: Usuario que compra el ticket
        seat: Asiento seleccionado
        function: Función para la cual se compra el ticket
        
    Returns:
        str: Código único del ticket
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
    Verifica si un asiento está disponible o reservado para una función específica
    
    Args:
        seat: Asiento a verificar
        function: Función para la cual se verifica la disponibilidad
        
    Raises:
        ValidationError: Si el asiento no está disponible o ya está reservado
    """
    try:
        if Ticket.objects.filter(seat=seat, booking__function=function, 
                               booking__status__in=['pending', 'paid']).exists():
            raise ValidationError("Este asiento ya está reservado para esta función")

        if not seat.seat_available:
            raise ValidationError("Este asiento no está disponible")
            
    except Exception as e:
        logger.error(f"Error checking seat availability: {str(e)}")
        raise


def validate_ticket_purchase(user, tickets_requested, function):
    """
    Valida y procesa la compra de entradas por un usuario para una función específica

    Args:
        user: Usuario que realiza la compra
        tickets_requested: Lista de tickets solicitados
        function: Función para la cual se compran las entradas
        
    Raises:
        ValidationError: Si se excede el límite de tickets por usuario
    """
    try:
        existing_tickets = Ticket.objects.filter(
            booking__user=user, 
            booking__function=function
        ).count()

        amount_ticket_requested = len(tickets_requested)

        if existing_tickets + amount_ticket_requested > MAX_TICKETS_PER_USER:
            raise ValidationError(
                f"No puedes comprar más de {MAX_TICKETS_PER_USER} tickets para una misma función"
            )
            
    except Exception as e:
        logger.error(f"Error validating ticket purchase: {str(e)}")
        raise


def check_capacity(booking, function, hall):
    """
    Verifica la disponibilidad de asientos en una sala para una función específica
    
    Args:
        booking: Reserva de asientos
        function: Función a verificar
        hall: Sala asociada a la función
        
    Returns:
        bool: True si hay capacidad disponible, False en caso contrario
    """
    try:
        total_booked_seats = Ticket.objects.filter(
            booking__function=function,
            booking__status__in=['pending', 'paid']
        ).count()
        
        return total_booked_seats < hall.capacity
        
    except Exception as e:
        logger.error(f"Error checking capacity: {str(e)}")
        raise


def release_expired_reservations():
    """
    Libera los asientos reservados si el pago no se completó en el tiempo establecido
    """
    try:
        expired_bookings = Booking.objects.filter(
            status='pending',
            reserved_at__lt=timezone.now() - timedelta(minutes=RESERVATION_EXPIRY_MINUTES)
        )

        for booking in expired_bookings:
            booking.status = 'cancelled'
            booking.save()
            logger.info(f"Released expired booking: {booking.id}")
            
    except Exception as e:
        logger.error(f"Error releasing expired reservations: {str(e)}")
        raise


def generate_qr_code(ticket):
    """
    Genera un código QR para el ticket con información esencial
    
    Args:
        ticket: Ticket para el cual se genera el QR
        
    Returns:
        str: Ruta del archivo QR generado
    """
    try:
        qr_data = f'Ticket ID: {ticket.id}, Código: {ticket.ticket_code}, Función: {ticket.booking.function}'
        qr = qrcode.make(qr_data)

        qr_path = f"{settings.MEDIA_ROOT}/qr_codes/ticket_{ticket.id}.png"
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        qr.save(qr_path)
        
        return qr_path
        
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        raise


def send_confirmation_email(ticket, qr_code_path):
    """
    Envía un correo de confirmación al usuario con el QR adjunto
    
    Args:
        ticket: Ticket para el cual se envía la confirmación
        qr_code_path: Ruta del archivo QR generado
    """
    try:
        subject = "Confirmación de compra - CineApp"
        message = (
            f'Hola {ticket.booking.user.username},\n\n'
            f'Tu compra ha sido confirmada para la función "{ticket.booking.function.movie.title}". '
            f'Adjuntamos tu código QR para el ingreso.\n\n'
            f'¡Gracias por elegirnos!'
        )
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[ticket.booking.user.email]
        )

        if os.path.exists(qr_code_path):
            email.attach_file(qr_code_path)
            
        email.send()
        logger.info(f"Confirmation email sent for ticket: {ticket.id}")
        
    except Exception as e:
        logger.error(f"Error sending confirmation email: {str(e)}")
        raise