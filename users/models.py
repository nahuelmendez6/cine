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

    is_admin = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)