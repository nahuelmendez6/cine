import datetime

from django.conf.locale.ar.formats import DATE_FORMAT
from django.test import TestCase
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cine.settings')
django.setup()

# Create your tests here.
from django.test import TestCase
from django.utils import timezone
from movies.models import Hall, Function, Movie
from users.models import CustomUser
from bookings.models import Seat, Booking, Ticket, Combo, ComboTicket

class BookingModelTests(TestCase):
    def setUp(self):
        """
        Se ejecuta antes de cada test para crear los objectos necesarios
        (usuario, funcion, sala, asiento y combo)
        """
        # Crear usuario de prueba
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')

        # Crear sala de cine (Hall)
        self.hall = Hall.objects.create(name='Sala 1', total_seats=100)

        # Crear película de prueba
        self.movie = Movie.objects.create(
            title='Película de prueba',
            poster = 'poster.jpg',
            synopsis = 'Sinopsis de la pelicula de prueba',
            duration = 120,
            genre = 'accion',
            classification = '+16',
            date_release ="2024-02-05",
            date_finish = "2024-02-15",
        )

        # Crear función de prueba
        self.function = Function.objects.create(
            movie=self.movie,
            function_date = "2024-02-05",
            function_time_start = datetime.datetime(2024, 2, 5, 16, 0),
            function_time_end = datetime.datetime(2024, 2, 5, 18, 0),
            price = 100,
            language = 'Doblada',
            format = '2D',
            hall = self.hall
        )

        # Crear asiento de prueba
        self.seat = Seat.objects.create(hall=self.hall, row='A', number=1)

        # Crear combo de prueba
        self.combo = Combo.objects.create(
            combo_name='Combo Popcorn',
            combo_description='Popcorn grande y bebida',
            combo_price=50.00
        )

    def test_booking_creation(self):
        # Crear una reserva
        booking = Booking.objects.create(
            user=self.user,
            function=self.function,
            total_price=100.00,
            status='pending'
        )
        self.assertEqual(booking.user.username, 'testuser')
        self.assertEqual(booking.function.movie.title, 'Película de prueba')
        self.assertEqual(booking.total_price, 100.00)
        self.assertEqual(booking.status, 'pending')

    def test_ticket_creation(self):
        # Crear una reserva
        booking = Booking.objects.create(
            user=self.user,
            function=self.function,
            total_price=100.00,
            status='pending'
        )

        # Crear un ticket
        ticket = Ticket.objects.create(
            booking=booking,
            seat=self.seat,
            ticket_code='ABC123'
        )
        self.assertEqual(ticket.booking, booking)
        self.assertEqual(ticket.seat, self.seat)
        self.assertEqual(ticket.ticket_code, 'ABC123')
        self.assertFalse(ticket.is_scanned)

    def test_combo_ticket_creation(self):
        # Crear una reserva
        booking = Booking.objects.create(
            user=self.user,
            function=self.function,
            total_price=150.00,
            status='pending'
        )

        # Crear un combo ticket
        combo_ticket = ComboTicket.objects.create(
            booking=booking,
            combo=self.combo,
            quantity=2,
            total_combo_price=100.00,
            combo_ticket_code='COMBO123'
        )
        self.assertEqual(combo_ticket.booking, booking)
        self.assertEqual(combo_ticket.combo, self.combo)
        self.assertEqual(combo_ticket.quantity, 2)
        self.assertEqual(combo_ticket.total_combo_price, 100.00)
        self.assertFalse(combo_ticket.is_scanned)
