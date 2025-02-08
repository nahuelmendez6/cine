import datetime

from django.conf.locale.ar.formats import DATE_FORMAT
from django.test import TestCase
import os
import django
from django.conf import settings
from rest_framework.exceptions import ValidationError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cine.settings')
django.setup()

# Create your tests here.
from django.test import TestCase
from django.utils import timezone
from movies.models import Hall, Function, Movie
from users.models import CustomUser
from bookings.models import Seat, Booking, Ticket, Combo, ComboTicket
from bookings.services import validate_ticket_purchase

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

class PurchaseTicketTest(TestCase):
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

        self.seat1 = Seat.objects.create(
            hall = self.hall,
            row = 'A',
            number = 1,
            seat_available = True,
        )
        self.seat2 = Seat.objects.create(
            hall=self.hall,
            row='A',
            number=2,
            seat_available=True,
        )
        self.seat3 = Seat.objects.create(
            hall=self.hall,
            row='A',
            number=3,
            seat_available=True,
        )
        self.seat4 = Seat.objects.create(
            hall=self.hall,
            row='A',
            number=4,
            seat_available=True,
        )
        self.seat5 = Seat.objects.create(
            hall=self.hall,
            row='A',
            number=5,
            seat_available=True,
        )
        self.seat6 = Seat.objects.create(
            hall=self.hall,
            row='A',
            number=6,
            seat_available=True,
        )
        self.seat7 = Seat.objects.create(
            hall=self.hall,
            row='A',
            number=7,
            seat_available=True,
        )
        self.seat8 = Seat.objects.create(
            hall=self.hall,
            row='A',
            number=8,
            seat_available=True,
        )
        self.seat9 = Seat.objects.create(
            hall=self.hall,
            row='A',
            number=9,
            seat_available=True,
        )
        self.seat10 = Seat.objects.create(
            hall=self.hall,
            row='A',
            number=10,
            seat_available=True,
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



    def test_validate_ticket_purchase_within_limit(self):
        """ Verifica que un usuario pueda comprar hasta el límite máximo de tickets """
        try:
            validate_ticket_purchase(self.user, tickets_requested=[self.seat1,self.seat2,self.seat3,
                                                                   self.seat4,self.seat5], function=self.function)
        except ValidationError:
            self.fail("validate_ticket_purchase() lanzó ValidationError inesperado")


    def test_validate_ticket_purchase_exceed_limit(self):
        """ verifica que no se puedan comprar más de 10 tickets """
        # Primero compra 5 tickets
        validate_ticket_purchase(self.user, tickets_requested=[self.seat1,self.seat2,self.seat3,
                                                                   self.seat4,self.seat5], function=self.function)

        # Ahora intenta comprar otros 6 (total 11)
        with self.assertRaises(ValidationError) as context:
            validate_ticket_purchase(self.user, tickets_requested=[self.seat1,self.seat2,self.seat3,
                                                                   self.seat4,self.seat5, self.seat6], function=self.function)
            self.assertIn("No puedes comprar más de 10 para una misma función", str(context.exception))

    def test_validate_ticker_purchase_exact_limit(self):
        """ Verifica que no pueda comprarse el limite especifico """
        try:
            validate_ticket_purchase(self.user, tickets_requested=[self.seat1,self.seat2,self.seat3,
                                                                   self.seat4,self.seat5, self.seat6,
                                                                   self.seat7, self.seat8, self.seat9,
                                                                   self.seat10], function=self.function)
        except ValidationError:
            self.fail("validate_ticket_purchase() lanzó ValidationError inesperadamente al intentar comprar exactamente 10 tickets.")


