from datetime import timedelta

from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now
from rest_framework.exceptions import AuthenticationFailed

from users.models import CustomUser


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(username=username)
            print(f"Usuario encontrado: {username}")  # Debug
            print(f"Contraseña recibida: {password}")  # Debug
            print(f"Hash almacenado: {user.password}")  # Debug

            # Verificar si el usuario está bloqueado
            if user.is_locked:
                user.unlock()  # Intenta desbloquear si el tiempo ha pasado
                if user.is_locked:
                    raise AuthenticationFailed({
                        'error': "Usuario bloqueado.",
                        'locked_until': user.lockout_time + timedelta(minutes=10)
                    })

            # Verificar contraseña
            is_valid = user.check_password(password)
            print(f"Resultado de check_password: {is_valid}")  # Debug
            
            if is_valid:
                if not user.is_active:
                    raise AuthenticationFailed("Tu cuenta está desactivada.")
                
                # Reset intentos fallidos si la autenticación es exitosa
                user.reset_failed_attempts()
                return user
            else:
                # Incrementar intentos fallidos
                user.increment_failed_attempts()
                attempts_left = 3 - user.failed_attempts
                raise AuthenticationFailed({
                    'error': 'Contraseña incorrecta.',
                    'attempts_left': attempts_left
                })

        except CustomUser.DoesNotExist:
            raise AuthenticationFailed("Usuario no encontrado")
        except Exception as e:
            print(f"Error en autenticación: {str(e)}")  # Debug
            raise AuthenticationFailed(str(e))

    def get_user(self, user_id):
        try:
            user = CustomUser.objects.get(pk=user_id)
            return user if user.is_active else None
        except CustomUser.DoesNotExist:
            return None