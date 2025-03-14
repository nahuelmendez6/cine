from datetime import timedelta

from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now

from users.models import CustomUser


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(username=username)

            # Verificar si el usuario está bloqueado
            if user.is_locked:
                user.unlock()  # Intenta desbloquear si el tiempo ha pasado
                if user.is_locked:
                    raise PermissionDenied({
                        'error': "Usuario bloqueado.",
                        'locked_until': user.lockout_time + timedelta(minutes=10)
                    })

            # Verificar contraseña
            if user.check_password(password):
                if not user.is_active:
                    raise PermissionDenied("Tu cuenta está desactivada.")
                
                # Reset intentos fallidos si la autenticación es exitosa
                user.reset_failed_attempts()
                return user
            else:
                # Incrementar intentos fallidos
                user.increment_failed_attempts()
                attempts_left = 3 - user.failed_attempts
                raise PermissionDenied({
                    'error': 'Contraseña incorrecta.',
                    'attempts_left': attempts_left
                })

        except CustomUser.DoesNotExist:
            # No revelamos si el usuario existe o no por seguridad
            return None

    def get_user(self, user_id):
        try:
            user = CustomUser.objects.get(pk=user_id)
            return user if user.is_active else None
        except CustomUser.DoesNotExist:
            return None