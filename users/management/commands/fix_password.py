from django.core.management.base import BaseCommand
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Fixes password hashing for all users'

    def handle(self, *args, **options):
        users = CustomUser.objects.all()
        for user in users:
            # Si la contraseña no está hasheada (no comienza con pbkdf2_sha256$)
            if not user.password.startswith('pbkdf2_sha256$'):
                # Guardamos la contraseña actual
                current_password = user.password
                # Establecemos la contraseña nuevamente (esto la hasheará)
                user.set_password(current_password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Password fixed for user {user.username}')) 