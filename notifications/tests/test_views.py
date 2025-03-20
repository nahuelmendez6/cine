import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

from .models import Notification, NotificationTemplate, NotificationPreference
from users.models import CustomUser
from movies.models import Movie, Function

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
def function(movie):
    return Function.objects.create(
        movie=movie,
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=1, hours=2)
    )

@pytest.fixture
def notification_template():
    return NotificationTemplate.objects.create(
        name='booking_confirmation',
        subject='Confirmación de Reserva',
        body='Tu reserva para {movie_title} ha sido confirmada.',
        notification_type='email'
    )

@pytest.fixture
def notification(user, function, notification_template):
    return Notification.objects.create(
        user=user,
        template=notification_template,
        context={'movie_title': function.movie.title},
        status='pending'
    )

class TestNotificationListView:
    def test_list_notifications_unauthorized(self, api_client):
        url = reverse('notifications:notification-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_notifications_empty(self, authenticated_client):
        url = reverse('notifications:notification-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_notifications_with_notifications(self, authenticated_client, notification):
        url = reverse('notifications:notification-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['template']['name'] == notification.template.name

class TestNotificationDetailView:
    def test_get_notification_detail_unauthorized(self, api_client, notification):
        url = reverse('notifications:notification-detail', kwargs={'pk': notification.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_notification_detail(self, authenticated_client, notification):
        url = reverse('notifications:notification-detail', kwargs={'pk': notification.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['template']['name'] == notification.template.name
        assert response.data['status'] == notification.status

    def test_get_notification_detail_not_found(self, authenticated_client):
        url = reverse('notifications:notification-detail', kwargs={'pk': 999})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestNotificationPreferenceView:
    def test_get_preferences_unauthorized(self, api_client):
        url = reverse('notifications:preference-detail')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_preferences(self, authenticated_client, user):
        preference = NotificationPreference.objects.create(
            user=user,
            email_enabled=True,
            push_enabled=True,
            sms_enabled=False
        )
        url = reverse('notifications:preference-detail')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email_enabled'] is True
        assert response.data['push_enabled'] is True
        assert response.data['sms_enabled'] is False

    def test_update_preferences(self, authenticated_client, user):
        preference = NotificationPreference.objects.create(
            user=user,
            email_enabled=True,
            push_enabled=True,
            sms_enabled=False
        )
        url = reverse('notifications:preference-detail')
        data = {
            'email_enabled': False,
            'push_enabled': True,
            'sms_enabled': True
        }
        response = authenticated_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email_enabled'] is False
        assert response.data['push_enabled'] is True
        assert response.data['sms_enabled'] is True

class TestNotificationTemplateListView:
    def test_list_templates_unauthorized(self, api_client):
        url = reverse('notifications:template-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_templates_empty(self, authenticated_client):
        url = reverse('notifications:template-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_templates_with_templates(self, authenticated_client, notification_template):
        url = reverse('notifications:template-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == notification_template.name

class TestNotificationTemplateDetailView:
    def test_get_template_detail_unauthorized(self, api_client, notification_template):
        url = reverse('notifications:template-detail', kwargs={'pk': notification_template.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_template_detail(self, authenticated_client, notification_template):
        url = reverse('notifications:template-detail', kwargs={'pk': notification_template.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == notification_template.name
        assert response.data['subject'] == notification_template.subject

    def test_get_template_detail_not_found(self, authenticated_client):
        url = reverse('notifications:template-detail', kwargs={'pk': 999})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND 