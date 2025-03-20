import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import Movie, Hall, Function, Genre, Actor, Director, Review
from .serializers import (
    MovieSerializer,
    HallSerializer,
    FunctionSerializer,
    GenreSerializer,
    ActorSerializer,
    DirectorSerializer,
    ReviewSerializer
)

@pytest.fixture
def genre():
    return Genre.objects.create(
        name='Action',
        description='Action movies'
    )

@pytest.fixture
def actor():
    return Actor.objects.create(
        name='John Doe',
        biography='Famous actor',
        birth_date=timezone.now() - timedelta(days=365*30)
    )

@pytest.fixture
def director():
    return Director.objects.create(
        name='Jane Smith',
        biography='Famous director',
        birth_date=timezone.now() - timedelta(days=365*40)
    )

@pytest.fixture
def movie(genre, actor, director):
    movie = Movie.objects.create(
        title='Test Movie',
        description='Test Description',
        duration=120,
        release_date=timezone.now(),
        rating=4.5,
        genre=genre
    )
    movie.actors.add(actor)
    movie.directors.add(director)
    return movie

@pytest.fixture
def hall():
    return Hall.objects.create(
        hall_name='Sala 1',
        rows=5,
        seats_per_row=10
    )

@pytest.fixture
def function(movie, hall):
    return Function.objects.create(
        movie=movie,
        hall=hall,
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=1, hours=2)
    )

class TestMovieSerializer:
    def test_movie_serializer_valid_data(self, genre, actor, director):
        data = {
            'title': 'Test Movie',
            'description': 'Test Description',
            'duration': 120,
            'release_date': timezone.now(),
            'rating': 4.5,
            'genre': genre.id,
            'actors': [actor.id],
            'directors': [director.id]
        }
        serializer = MovieSerializer(data=data)
        assert serializer.is_valid()
        movie = serializer.save()
        assert movie.title == data['title']
        assert movie.duration == data['duration']
        assert movie.rating == data['rating']
        assert movie.genre == genre
        assert actor in movie.actors.all()
        assert director in movie.directors.all()

    def test_movie_serializer_invalid_duration(self, genre):
        data = {
            'title': 'Test Movie',
            'description': 'Test Description',
            'duration': 0,  # Duración inválida
            'release_date': timezone.now(),
            'rating': 4.5,
            'genre': genre.id
        }
        serializer = MovieSerializer(data=data)
        assert not serializer.is_valid()
        assert 'duration' in serializer.errors

    def test_movie_serializer_invalid_rating(self, genre):
        data = {
            'title': 'Test Movie',
            'description': 'Test Description',
            'duration': 120,
            'release_date': timezone.now(),
            'rating': 6.0,  # Rating inválido
            'genre': genre.id
        }
        serializer = MovieSerializer(data=data)
        assert not serializer.is_valid()
        assert 'rating' in serializer.errors

class TestHallSerializer:
    def test_hall_serializer_valid_data(self):
        data = {
            'hall_name': 'Sala 1',
            'rows': 5,
            'seats_per_row': 10
        }
        serializer = HallSerializer(data=data)
        assert serializer.is_valid()
        hall = serializer.save()
        assert hall.hall_name == data['hall_name']
        assert hall.rows == data['rows']
        assert hall.seats_per_row == data['seats_per_row']

    def test_hall_serializer_invalid_rows(self):
        data = {
            'hall_name': 'Sala 1',
            'rows': 0,  # Filas inválidas
            'seats_per_row': 10
        }
        serializer = HallSerializer(data=data)
        assert not serializer.is_valid()
        assert 'rows' in serializer.errors

    def test_hall_serializer_invalid_seats_per_row(self):
        data = {
            'hall_name': 'Sala 1',
            'rows': 5,
            'seats_per_row': 0  # Asientos por fila inválidos
        }
        serializer = HallSerializer(data=data)
        assert not serializer.is_valid()
        assert 'seats_per_row' in serializer.errors

class TestFunctionSerializer:
    def test_function_serializer_valid_data(self, movie, hall):
        data = {
            'movie': movie.id,
            'hall': hall.id,
            'start_time': timezone.now() + timedelta(days=1),
            'end_time': timezone.now() + timedelta(days=1, hours=2)
        }
        serializer = FunctionSerializer(data=data)
        assert serializer.is_valid()
        function = serializer.save()
        assert function.movie == movie
        assert function.hall == hall
        assert function.start_time == data['start_time']
        assert function.end_time == data['end_time']

    def test_function_serializer_invalid_time(self, movie, hall):
        data = {
            'movie': movie.id,
            'hall': hall.id,
            'start_time': timezone.now(),
            'end_time': timezone.now() - timedelta(hours=1)  # Tiempo final antes del inicio
        }
        serializer = FunctionSerializer(data=data)
        assert not serializer.is_valid()
        assert 'end_time' in serializer.errors

class TestGenreSerializer:
    def test_genre_serializer_valid_data(self):
        data = {
            'name': 'Action',
            'description': 'Action movies'
        }
        serializer = GenreSerializer(data=data)
        assert serializer.is_valid()
        genre = serializer.save()
        assert genre.name == data['name']
        assert genre.description == data['description']

class TestActorSerializer:
    def test_actor_serializer_valid_data(self):
        data = {
            'name': 'John Doe',
            'biography': 'Famous actor',
            'birth_date': timezone.now() - timedelta(days=365*30)
        }
        serializer = ActorSerializer(data=data)
        assert serializer.is_valid()
        actor = serializer.save()
        assert actor.name == data['name']
        assert actor.biography == data['biography']
        assert actor.birth_date == data['birth_date']

class TestDirectorSerializer:
    def test_director_serializer_valid_data(self):
        data = {
            'name': 'Jane Smith',
            'biography': 'Famous director',
            'birth_date': timezone.now() - timedelta(days=365*40)
        }
        serializer = DirectorSerializer(data=data)
        assert serializer.is_valid()
        director = serializer.save()
        assert director.name == data['name']
        assert director.biography == data['biography']
        assert director.birth_date == data['birth_date']

class TestReviewSerializer:
    def test_review_serializer_valid_data(self, movie, user):
        data = {
            'movie': movie.id,
            'user': user.id,
            'rating': 5,
            'comment': 'Great movie!'
        }
        serializer = ReviewSerializer(data=data)
        assert serializer.is_valid()
        review = serializer.save()
        assert review.movie == movie
        assert review.user == user
        assert review.rating == data['rating']
        assert review.comment == data['comment']

    def test_review_serializer_invalid_rating(self, movie, user):
        data = {
            'movie': movie.id,
            'user': user.id,
            'rating': 6,  # Rating inválido
            'comment': 'Great movie!'
        }
        serializer = ReviewSerializer(data=data)
        assert not serializer.is_valid()
        assert 'rating' in serializer.errors 