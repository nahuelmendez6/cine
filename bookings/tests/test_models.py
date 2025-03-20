import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from movies.models import Hall, Function, Movie
from users.models import CustomUser
from .models import Seat, Booking, Ticket, Combo, ComboTicket

@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def hall():
    return Hall.objects.create(
        hall_name='Sala 1',
        rows=5,
        seats_per_row=10
    )

@pytest.fixture
def movie():
    return Movie.objects.create(
        title='Test Movie',
        description='Test Description',
        duration=120,
        release_date=timezone.now(),
        rating=4.5,
        genre='Action'
    )

@pytest.fixture
def function(hall, movie):
    return Function.objects.create(
        movie=movie,
        hall=hall,
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=1, hours=2)
    )

@pytest.fixture
def seat(hall):
    return Seat.objects.create(
        hall=hall,
        row='A',
        number=1
    )

class TestSeat:
    def test_seat_creation(self, hall):
        seat = Seat.objects.create(
            hall=hall,
            row='A',
            number=1
        )
        assert seat.row == 'A'
        assert seat.number == 1
        assert seat.seat_available is True
        assert str(seat) == f'Fila {seat.row} - Asiento {seat.number}'

    def test_seat_availability(self, seat):
        assert seat.seat_available is True
        seat.seat_available = False
        seat.save()
        assert seat.seat_available is False

class TestBooking:
    def test_booking_creation(self, user, function):
        booking = Booking.objects.create(
            user=user,
            function=function,
            status='pending'
        )
        assert booking.user == user
        assert booking.function == function
        assert booking.status == 'pending'
        assert booking.created_at is not None

    def test_booking_status_transition(self, user, function):
        booking = Booking.objects.create(
            user=user,
            function=function,
            status='pending'
        )
        booking.status = 'paid'
        booking.save()
        assert booking.status == 'paid'

    def test_booking_total_price_calculation(self, user, function):
        booking = Booking.objects.create(
            user=user,
            function=function,
            status='pending'
        )
        # Crear tickets para la reserva
        seat1 = Seat.objects.create(hall=function.hall, row='A', number=1)
        seat2 = Seat.objects.create(hall=function.hall, row='A', number=2)
        
        Ticket.objects.create(booking=booking, seat=seat1)
        Ticket.objects.create(booking=booking, seat=seat2)
        
        # El precio total debería ser el precio de la función * número de tickets
        expected_total = function.price * 2
        assert booking.total_price == expected_total

class TestTicket:
    def test_ticket_creation(self, booking, seat):
        ticket = Ticket.objects.create(
            booking=booking,
            seat=seat,
            ticket_code='TEST-123'
        )
        assert ticket.booking == booking
        assert ticket.seat == seat
        assert ticket.ticket_code == 'TEST-123'
        assert ticket.issued_at is not None
        assert ticket.is_scanned is False

    def test_ticket_scanning(self, booking, seat):
        ticket = Ticket.objects.create(
            booking=booking,
            seat=seat,
            ticket_code='TEST-123'
        )
        ticket.is_scanned = True
        ticket.save()
        assert ticket.is_scanned is True

class TestCombo:
    def test_combo_creation(self):
        combo = Combo.objects.create(
            combo_name='Combo Familiar',
            combo_description='2 bebidas grandes + 1 palomitas grandes',
            combo_price=25.00
        )
        assert combo.combo_name == 'Combo Familiar'
        assert combo.combo_price == 25.00
        assert str(combo) == combo.combo_name

class TestComboTicket:
    def test_combo_ticket_creation(self, booking):
        combo = Combo.objects.create(
            combo_name='Combo Individual',
            combo_description='1 bebida + 1 palomitas',
            combo_price=15.00
        )
        combo_ticket = ComboTicket.objects.create(
            booking=booking,
            combo=combo,
            quantity=2,
            total_combo_price=30.00,
            combo_ticket_code='CMB-123'
        )
        assert combo_ticket.booking == booking
        assert combo_ticket.combo == combo
        assert combo_ticket.quantity == 2
        assert combo_ticket.total_combo_price == 30.00
        assert combo_ticket.combo_ticket_code == 'CMB-123'
        assert combo_ticket.issued_at is not None
        assert combo_ticket.is_scanned is False

    def test_combo_ticket_total_price_calculation(self, booking):
        combo = Combo.objects.create(
            combo_name='Combo Individual',
            combo_description='1 bebida + 1 palomitas',
            combo_price=15.00
        )
        combo_ticket = ComboTicket.objects.create(
            booking=booking,
            combo=combo,
            quantity=2,
            combo_ticket_code='CMB-123'
        )
        # El precio total debería ser el precio del combo * cantidad
        expected_total = combo.combo_price * 2
        assert combo_ticket.total_combo_price == expected_total 