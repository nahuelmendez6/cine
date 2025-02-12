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
                if now() > user.lockout_time + timedelta(minutes=15):
                    # Desbloquear automaticamente despues del tiempod e espera
                    user.unlock()
                else:
                    raise PermissionDenied("Tu cuenta está temporalmente bloqueada")

            if user.check_password(password):
                user.failed_attemps = 0 # Resetear intentos fallidos
                user.save()
                return user
        except CustomUser.DoesNotExist:
            return None