import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from movies.models import Movie
from movies.serializers import MovieSerializer

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def movie_data():
    return {
        'title': 'Test Movie',
        'description': 'Test Description',
        'duration': 120,
        'release_date': timezone.now().date(),
        'rating': 4.5,
        'genre': 'ACTION',
        'is_active': True
    }

@pytest.fixture
def create_movie(movie_data):
    return Movie.objects.create(**movie_data)

@pytest.mark.django_db
class TestMovieViewSet:
    def test_list_movies(self, api_client, create_movie):
        url = reverse('movie-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_retrieve_movie(self, api_client, create_movie):
        url = reverse('movie-detail', kwargs={'pk': create_movie.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == create_movie.title

    def test_create_movie(self, api_client, movie_data):
        url = reverse('movie-list')
        response = api_client.post(url, movie_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Movie.objects.count() == 1
        assert Movie.objects.get().title == movie_data['title']

    def test_update_movie(self, api_client, create_movie):
        url = reverse('movie-detail', kwargs={'pk': create_movie.id})
        updated_data = {'title': 'Updated Movie Title'}
        response = api_client.patch(url, updated_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert Movie.objects.get(id=create_movie.id).title == updated_data['title']

    def test_delete_movie(self, api_client, create_movie):
        url = reverse('movie-detail', kwargs={'pk': create_movie.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Movie.objects.count() == 0

    def test_trending_movies(self, api_client):
        # Create multiple movies with different ratings
        for i in range(15):
            Movie.objects.create(
                title=f'Movie {i}',
                description='Description',
                duration=120,
                release_date=timezone.now().date(),
                rating=float(i/2),
                genre='ACTION',
                is_active=True
            )

        url = reverse('movie-trending')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10  # Should return top 10
        # Verify ordering
        ratings = [movie['rating'] for movie in response.data]
        assert ratings == sorted(ratings, reverse=True)

    def test_upcoming_movies(self, api_client):
        # Create movies with different release dates
        future_date = timezone.now().date() + timezone.timedelta(days=10)
        past_date = timezone.now().date() - timezone.timedelta(days=10)
        
        Movie.objects.create(
            title='Past Movie',
            description='Description',
            duration=120,
            release_date=past_date,
            rating=4.5,
            genre='ACTION',
            is_active=True
        )
        
        future_movie = Movie.objects.create(
            title='Future Movie',
            description='Description',
            duration=120,
            release_date=future_date,
            rating=4.5,
            genre='ACTION',
            is_active=True
        )

        url = reverse('movie-upcoming')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == future_movie.title 