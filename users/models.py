from datetime import timezone, timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):

    """
    Esta clase customiza la clase User por defecto de Django
    para diferenciar entre un usuario administrador del cine
    y un usuario final o cliente
    """

    email = models.EmailField(unique=True)  # Forzamos a que cada usuario tegna en mail unico
    is_admin = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)
    failed_attemps = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    lockout_time = models.DateTimeField(null=True, blank=True)

    def unlock(self):
        """ Desbloquea el usuario después del tiempo de espera """
        if self.is_locked and self.lockout_time:
            if timezone.now() > self.lockout_time + timedelta(minutes=15):
                self.is_locked = False
                self.failed_attemps = 0
                self.save()
