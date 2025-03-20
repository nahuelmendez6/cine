import pytest
from django.utils import timezone
from datetime import timedelta

from movies.models import Hall, Function, Movie
from users.models import CustomUser
from .models import Seat, Booking

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