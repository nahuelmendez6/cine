import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

from .models import Movie, Hall, Function, Genre, Actor, Director, Review
from users.models import CustomUser

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

class TestMovieListView:
    def test_list_movies_unauthorized(self, api_client):
        url = reverse('movies:movie-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_movies_empty(self, authenticated_client):
        url = reverse('movies:movie-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_movies_with_movies(self, authenticated_client, movie):
        url = reverse('movies:movie-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == movie.title

class TestMovieDetailView:
    def test_get_movie_detail_unauthorized(self, api_client, movie):
        url = reverse('movies:movie-detail', kwargs={'pk': movie.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_movie_detail(self, authenticated_client, movie):
        url = reverse('movies:movie-detail', kwargs={'pk': movie.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == movie.title
        assert response.data['description'] == movie.description

    def test_get_movie_detail_not_found(self, authenticated_client):
        url = reverse('movies:movie-detail', kwargs={'pk': 999})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestFunctionListView:
    def test_list_functions_unauthorized(self, api_client):
        url = reverse('movies:function-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_functions_empty(self, authenticated_client):
        url = reverse('movies:function-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_functions_with_functions(self, authenticated_client, function):
        url = reverse('movies:function-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['movie']['title'] == function.movie.title

class TestFunctionDetailView:
    def test_get_function_detail_unauthorized(self, api_client, function):
        url = reverse('movies:function-detail', kwargs={'pk': function.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_function_detail(self, authenticated_client, function):
        url = reverse('movies:function-detail', kwargs={'pk': function.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['movie']['title'] == function.movie.title
        assert response.data['hall']['hall_name'] == function.hall.hall_name

    def test_get_function_detail_not_found(self, authenticated_client):
        url = reverse('movies:function-detail', kwargs={'pk': 999})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestReviewListView:
    def test_list_reviews_unauthorized(self, api_client, movie):
        url = reverse('movies:review-list', kwargs={'movie_pk': movie.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_reviews_empty(self, authenticated_client, movie):
        url = reverse('movies:review-list', kwargs={'movie_pk': movie.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_reviews_with_reviews(self, authenticated_client, movie, user):
        review = Review.objects.create(
            movie=movie,
            user=user,
            rating=5,
            comment='Great movie!'
        )
        url = reverse('movies:review-list', kwargs={'movie_pk': movie.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['comment'] == review.comment

class TestReviewCreateView:
    def test_create_review_unauthorized(self, api_client, movie):
        url = reverse('movies:review-create', kwargs={'movie_pk': movie.pk})
        data = {
            'rating': 5,
            'comment': 'Great movie!'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_review_success(self, authenticated_client, movie):
        url = reverse('movies:review-create', kwargs={'movie_pk': movie.pk})
        data = {
            'rating': 5,
            'comment': 'Great movie!'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['comment'] == data['comment']
        assert Review.objects.count() == 1

    def test_create_review_invalid_rating(self, authenticated_client, movie):
        url = reverse('movies:review-create', kwargs={'movie_pk': movie.pk})
        data = {
            'rating': 6,  # Rating inválido
            'comment': 'Great movie!'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

class TestHallListView:
    def test_list_halls_unauthorized(self, api_client):
        url = reverse('movies:hall-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_halls_empty(self, authenticated_client):
        url = reverse('movies:hall-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_halls_with_halls(self, authenticated_client, hall):
        url = reverse('movies:hall-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['hall_name'] == hall.hall_name 