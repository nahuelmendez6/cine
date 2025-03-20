import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import Notification, NotificationTemplate, NotificationPreference
from .serializers import (
    NotificationSerializer,
    NotificationTemplateSerializer,
    NotificationPreferenceSerializer
)
from users.models import CustomUser
from movies.models import Movie, Function

@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
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

class TestNotificationSerializer:
    def test_notification_serializer_valid_data(self, user, function, notification_template):
        data = {
            'user': user.id,
            'template': notification_template.id,
            'context': {'movie_title': function.movie.title},
            'status': 'pending'
        }
        serializer = NotificationSerializer(data=data)
        assert serializer.is_valid()
        notification = serializer.save()
        assert notification.user == user
        assert notification.template == notification_template
        assert notification.context == data['context']
        assert notification.status == data['status']

    def test_notification_serializer_invalid_status(self, user, function, notification_template):
        data = {
            'user': user.id,
            'template': notification_template.id,
            'context': {'movie_title': function.movie.title},
            'status': 'invalid_status'  # Estado inválido
        }
        serializer = NotificationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'status' in serializer.errors

    def test_notification_serializer_invalid_template(self, user, function):
        data = {
            'user': user.id,
            'template': 999,  # ID de template inexistente
            'context': {'movie_title': function.movie.title},
            'status': 'pending'
        }
        serializer = NotificationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'template' in serializer.errors

class TestNotificationTemplateSerializer:
    def test_template_serializer_valid_data(self):
        data = {
            'name': 'booking_confirmation',
            'subject': 'Confirmación de Reserva',
            'body': 'Tu reserva para {movie_title} ha sido confirmada.',
            'notification_type': 'email'
        }
        serializer = NotificationTemplateSerializer(data=data)
        assert serializer.is_valid()
        template = serializer.save()
        assert template.name == data['name']
        assert template.subject == data['subject']
        assert template.body == data['body']
        assert template.notification_type == data['notification_type']

    def test_template_serializer_invalid_type(self):
        data = {
            'name': 'invalid_type',
            'subject': 'Test Subject',
            'body': 'Test Body',
            'notification_type': 'invalid_type'  # Tipo inválido
        }
        serializer = NotificationTemplateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'notification_type' in serializer.errors

    def test_template_serializer_format_body(self, notification_template):
        context = {'movie_title': 'Test Movie'}
        formatted_body = notification_template.format_body(context)
        assert formatted_body == 'Tu reserva para Test Movie ha sido confirmada.'

class TestNotificationPreferenceSerializer:
    def test_preference_serializer_valid_data(self, user):
        data = {
            'user': user.id,
            'email_enabled': True,
            'push_enabled': True,
            'sms_enabled': False
        }
        serializer = NotificationPreferenceSerializer(data=data)
        assert serializer.is_valid()
        preference = serializer.save()
        assert preference.user == user
        assert preference.email_enabled is True
        assert preference.push_enabled is True
        assert preference.sms_enabled is False

    def test_preference_serializer_update(self, user):
        preference = NotificationPreference.objects.create(
            user=user,
            email_enabled=True,
            push_enabled=True,
            sms_enabled=False
        )
        data = {
            'email_enabled': False,
            'push_enabled': True,
            'sms_enabled': True
        }
        serializer = NotificationPreferenceSerializer(preference, data=data, partial=True)
        assert serializer.is_valid()
        updated_preference = serializer.save()
        assert updated_preference.email_enabled is False
        assert updated_preference.push_enabled is True
        assert updated_preference.sms_enabled is True

    def test_preference_serializer_unique_user(self, user):
        # Crear primera preferencia
        NotificationPreference.objects.create(
            user=user,
            email_enabled=True,
            push_enabled=True,
            sms_enabled=False
        )
        # Intentar crear segunda preferencia para el mismo usuario
        data = {
            'user': user.id,
            'email_enabled': True,
            'push_enabled': True,
            'sms_enabled': False
        }
        serializer = NotificationPreferenceSerializer(data=data)
        assert not serializer.is_valid()
        assert 'user' in serializer.errors 