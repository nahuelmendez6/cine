import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import Movie, Hall, Function, Genre, Actor, Director, Review

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

class TestMovie:
    def test_movie_creation(self, genre, actor, director):
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
        
        assert movie.title == 'Test Movie'
        assert movie.duration == 120
        assert movie.rating == 4.5
        assert movie.genre == genre
        assert actor in movie.actors.all()
        assert director in movie.directors.all()
        assert str(movie) == movie.title

    def test_movie_duration_validation(self, genre):
        with pytest.raises(ValidationError):
            movie = Movie.objects.create(
                title='Test Movie',
                description='Test Description',
                duration=0,  # Duración inválida
                release_date=timezone.now(),
                rating=4.5,
                genre=genre
            )
            movie.full_clean()

    def test_movie_rating_validation(self, genre):
        with pytest.raises(ValidationError):
            movie = Movie.objects.create(
                title='Test Movie',
                description='Test Description',
                duration=120,
                release_date=timezone.now(),
                rating=6.0,  # Rating inválido
                genre=genre
            )
            movie.full_clean()

class TestHall:
    def test_hall_creation(self):
        hall = Hall.objects.create(
            hall_name='Sala 1',
            rows=5,
            seats_per_row=10
        )
        assert hall.hall_name == 'Sala 1'
        assert hall.rows == 5
        assert hall.seats_per_row == 10
        assert str(hall) == hall.hall_name

    def test_hall_rows_validation(self):
        with pytest.raises(ValidationError):
            hall = Hall.objects.create(
                hall_name='Sala 1',
                rows=0,  # Filas inválidas
                seats_per_row=10
            )
            hall.full_clean()

    def test_hall_seats_per_row_validation(self):
        with pytest.raises(ValidationError):
            hall = Hall.objects.create(
                hall_name='Sala 1',
                rows=5,
                seats_per_row=0  # Asientos por fila inválidos
            )
            hall.full_clean()

class TestFunction:
    def test_function_creation(self, movie, hall):
        function = Function.objects.create(
            movie=movie,
            hall=hall,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2)
        )
        assert function.movie == movie
        assert function.hall == hall
        assert function.start_time is not None
        assert function.end_time is not None
        assert str(function) == f'{function.movie.title} - {function.hall.hall_name}'

    def test_function_time_validation(self, movie, hall):
        with pytest.raises(ValidationError):
            function = Function.objects.create(
                movie=movie,
                hall=hall,
                start_time=timezone.now(),
                end_time=timezone.now() - timedelta(hours=1)  # Tiempo final antes del inicio
            )
            function.full_clean()

class TestGenre:
    def test_genre_creation(self):
        genre = Genre.objects.create(
            name='Action',
            description='Action movies'
        )
        assert genre.name == 'Action'
        assert genre.description == 'Action movies'
        assert str(genre) == genre.name

class TestActor:
    def test_actor_creation(self):
        actor = Actor.objects.create(
            name='John Doe',
            biography='Famous actor',
            birth_date=timezone.now() - timedelta(days=365*30)
        )
        assert actor.name == 'John Doe'
        assert actor.biography == 'Famous actor'
        assert actor.birth_date is not None
        assert str(actor) == actor.name

class TestDirector:
    def test_director_creation(self):
        director = Director.objects.create(
            name='Jane Smith',
            biography='Famous director',
            birth_date=timezone.now() - timedelta(days=365*40)
        )
        assert director.name == 'Jane Smith'
        assert director.biography == 'Famous director'
        assert director.birth_date is not None
        assert str(director) == director.name

class TestReview:
    def test_review_creation(self, movie, user):
        review = Review.objects.create(
            movie=movie,
            user=user,
            rating=5,
            comment='Great movie!'
        )
        assert review.movie == movie
        assert review.user == user
        assert review.rating == 5
        assert review.comment == 'Great movie!'
        assert review.created_at is not None
        assert str(review) == f'Review for {review.movie.title} by {review.user.username}'

    def test_review_rating_validation(self, movie, user):
        with pytest.raises(ValidationError):
            review = Review.objects.create(
                movie=movie,
                user=user,
                rating=6,  # Rating inválido
                comment='Great movie!'
            )
            review.full_clean() 