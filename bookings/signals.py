from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Ticket
from bookings.services import send_confirmation_email, generate_qr_code

@receiver(post_save, sender=Ticket)
def process_ticket_creation(sender, instance, created, **kwargs):
    """
    Envía un correo de confimación y genera un qr cuando se crea un ticket
    """
    if created:
        # Generar codigo QR
        qr_code_path = generate_qr_code(instance)

        # Enviar correo de confirmación con qr adjunto
        send_confirmation_email(instance, qr_code_path)