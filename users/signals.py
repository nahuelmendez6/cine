from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from django.utils.timezone import now
from django.conf import settings
from users.models import CustomUser

MAX_FAILED_ATTEMPS = 5

@receiver(user_login_failed)
def login_failed_handler(sender, credentials, **kwargs):
    username = credentials.get('username')
    try:
        user = CustomUser.objects.get(username=username)

        # Incrementar el contador de intentos fallidos
        user.failed_attemps += 1

        if user.failed_attemps >= MAX_FAILED_ATTEMPS:
            user.is_locked = True
            user.lockout_time = now()

        user.save()
    except CustomUser.DoesNotExist:
        pass