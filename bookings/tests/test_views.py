import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

from movies.models import Hall, Function, Movie
from users.models import CustomUser
from .models import Seat, Booking, Ticket, Combo, ComboTicket

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

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

class TestCreateBookingView:
    def test_create_booking_unauthorized(self, api_client, function):
        url = reverse('bookings:create-booking')
        data = {
            'function': function.id,
            'status': 'pending'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_booking_success(self, authenticated_client, function):
        url = reverse('bookings:create-booking')
        data = {
            'function': function.id,
            'status': 'pending'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'booking_id' in response.data
        assert Booking.objects.count() == 1

    def test_create_booking_invalid_data(self, authenticated_client):
        url = reverse('bookings:create-booking')
        data = {
            'function': 999,  # ID inexistente
            'status': 'pending'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

class TestSelectSeatsView:
    def test_select_seats_unauthorized(self, api_client, booking, seat):
        url = reverse('bookings:select-seats')
        data = {
            'booking_id': booking.id,
            'seats': [seat.id]
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_select_seats_success(self, authenticated_client, booking, seat):
        url = reverse('bookings:select-seats')
        data = {
            'booking_id': booking.id,
            'seats': [seat.id]
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tickets' in response.data
        assert Ticket.objects.count() == 1
        assert not seat.seat_available

    def test_select_seats_invalid_booking(self, authenticated_client, seat):
        url = reverse('bookings:select-seats')
        data = {
            'booking_id': 999,  # ID inexistente
            'seats': [seat.id]
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestAddComboView:
    @pytest.fixture
    def combo(self):
        return Combo.objects.create(
            combo_name='Combo Individual',
            combo_description='1 bebida + 1 palomitas',
            combo_price=15.00
        )

    def test_add_combo_unauthorized(self, api_client, booking, combo):
        url = reverse('bookings:add-combo')
        data = {
            'booking_id': booking.id,
            'combo_id': combo.id,
            'quantity': 2
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_combo_success(self, authenticated_client, booking, combo):
        url = reverse('bookings:add-combo')
        data = {
            'booking_id': booking.id,
            'combo_id': combo.id,
            'quantity': 2
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'combo_ticket' in response.data
        assert ComboTicket.objects.count() == 1

    def test_add_combo_invalid_booking(self, authenticated_client, combo):
        url = reverse('bookings:add-combo')
        data = {
            'booking_id': 999,  # ID inexistente
            'combo_id': combo.id,
            'quantity': 2
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestMyBookingsView:
    def test_my_bookings_unauthorized(self, api_client):
        url = reverse('bookings:my-bookings')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_my_bookings_empty(self, authenticated_client):
        url = reverse('bookings:my-bookings')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_my_bookings_with_bookings(self, authenticated_client, booking):
        url = reverse('bookings:my-bookings')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == booking.id

class TestCancelBookingView:
    def test_cancel_booking_unauthorized(self, api_client, booking):
        url = reverse('bookings:cancel-booking', kwargs={'booking_id': booking.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cancel_booking_success(self, authenticated_client, booking, seat):
        # Crear un ticket para la reserva
        Ticket.objects.create(
            booking=booking,
            seat=seat,
            ticket_code='TEST-123'
        )
        
        url = reverse('bookings:cancel-booking', kwargs={'booking_id': booking.id})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que la reserva fue cancelada
        booking.refresh_from_db()
        assert booking.status == 'cancelled'
        
        # Verificar que los asientos fueron liberados
        seat.refresh_from_db()
        assert seat.seat_available is True

    def test_cancel_booking_not_found(self, authenticated_client):
        url = reverse('bookings:cancel-booking', kwargs={'booking_id': 999})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND 