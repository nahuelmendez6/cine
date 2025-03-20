import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from movies.models import Hall, Function, Movie
from users.models import CustomUser
from .models import Seat, Booking, Ticket, Combo, ComboTicket
from .serializers import (
    SeatSerializer,
    BookingSerializer,
    TicketSerializer,
    ComboSerializer,
    ComboTicketSerializer
)

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

@pytest.fixture
def booking(user, function):
    return Booking.objects.create(
        user=user,
        function=function,
        status='pending'
    )

class TestSeatSerializer:
    def test_seat_serializer_valid_data(self, hall):
        data = {
            'hall': hall.id,
            'row': 'A',
            'number': 1,
            'seat_available': True
        }
        serializer = SeatSerializer(data=data)
        assert serializer.is_valid()
        seat = serializer.save()
        assert seat.row == 'A'
        assert seat.number == 1
        assert seat.seat_available is True

    def test_seat_serializer_invalid_row(self, hall):
        data = {
            'hall': hall.id,
            'row': 'Z',  # Fila inválida
            'number': 1,
            'seat_available': True
        }
        serializer = SeatSerializer(data=data)
        assert not serializer.is_valid()
        assert 'row' in serializer.errors

    def test_seat_serializer_invalid_number(self, hall):
        data = {
            'hall': hall.id,
            'row': 'A',
            'number': 999,  # Número inválido
            'seat_available': True
        }
        serializer = SeatSerializer(data=data)
        assert not serializer.is_valid()
        assert 'number' in serializer.errors

class TestBookingSerializer:
    def test_booking_serializer_valid_data(self, user, function):
        data = {
            'user': user.id,
            'function': function.id,
            'status': 'pending'
        }
        serializer = BookingSerializer(data=data)
        assert serializer.is_valid()
        booking = serializer.save()
        assert booking.user == user
        assert booking.function == function
        assert booking.status == 'pending'

    def test_booking_serializer_invalid_status(self, user, function):
        data = {
            'user': user.id,
            'function': function.id,
            'status': 'invalid_status'
        }
        serializer = BookingSerializer(data=data)
        assert not serializer.is_valid()
        assert 'status' in serializer.errors

    def test_booking_serializer_invalid_function(self, user):
        data = {
            'user': user.id,
            'function': 999,  # ID inexistente
            'status': 'pending'
        }
        serializer = BookingSerializer(data=data)
        assert not serializer.is_valid()
        assert 'function' in serializer.errors

class TestTicketSerializer:
    def test_ticket_serializer_valid_data(self, booking, seat):
        data = {
            'booking': booking.id,
            'seat': seat.id,
            'ticket_code': 'TEST-123'
        }
        serializer = TicketSerializer(data=data)
        assert serializer.is_valid()
        ticket = serializer.save()
        assert ticket.booking == booking
        assert ticket.seat == seat
        assert ticket.ticket_code == 'TEST-123'

    def test_ticket_serializer_invalid_seat(self, booking):
        data = {
            'booking': booking.id,
            'seat': 999,  # ID inexistente
            'ticket_code': 'TEST-123'
        }
        serializer = TicketSerializer(data=data)
        assert not serializer.is_valid()
        assert 'seat' in serializer.errors

    def test_ticket_serializer_invalid_booking(self, seat):
        data = {
            'booking': 999,  # ID inexistente
            'seat': seat.id,
            'ticket_code': 'TEST-123'
        }
        serializer = TicketSerializer(data=data)
        assert not serializer.is_valid()
        assert 'booking' in serializer.errors

class TestComboSerializer:
    def test_combo_serializer_valid_data(self):
        data = {
            'combo_name': 'Combo Individual',
            'combo_description': '1 bebida + 1 palomitas',
            'combo_price': 15.00
        }
        serializer = ComboSerializer(data=data)
        assert serializer.is_valid()
        combo = serializer.save()
        assert combo.combo_name == 'Combo Individual'
        assert combo.combo_price == 15.00

    def test_combo_serializer_invalid_price(self):
        data = {
            'combo_name': 'Combo Individual',
            'combo_description': '1 bebida + 1 palomitas',
            'combo_price': -10.00  # Precio negativo
        }
        serializer = ComboSerializer(data=data)
        assert not serializer.is_valid()
        assert 'combo_price' in serializer.errors

class TestComboTicketSerializer:
    def test_combo_ticket_serializer_valid_data(self, booking):
        combo = Combo.objects.create(
            combo_name='Combo Individual',
            combo_description='1 bebida + 1 palomitas',
            combo_price=15.00
        )
        data = {
            'booking': booking.id,
            'combo': combo.id,
            'quantity': 2
        }
        serializer = ComboTicketSerializer(data=data)
        assert serializer.is_valid()
        combo_ticket = serializer.save()
        assert combo_ticket.booking == booking
        assert combo_ticket.combo == combo
        assert combo_ticket.quantity == 2
        assert combo_ticket.total_combo_price == 30.00

    def test_combo_ticket_serializer_invalid_quantity(self, booking):
        combo = Combo.objects.create(
            combo_name='Combo Individual',
            combo_description='1 bebida + 1 palomitas',
            combo_price=15.00
        )
        data = {
            'booking': booking.id,
            'combo': combo.id,
            'quantity': 0  # Cantidad inválida
        }
        serializer = ComboTicketSerializer(data=data)
        assert not serializer.is_valid()
        assert 'quantity' in serializer.errors 