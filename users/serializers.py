from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        try:
            user = CustomUser.objects.get(username=username)

            # Verificar si el usuario no está bloquado
            if user.is_locked:
                if user.unlock(): # Desbloqueo automático si el tiempo ha pasado
                    pass
                else:
                    raise PermissionDenied("Tu cuenta está temporalmente bloqueada.")

            # Autenticar usuario
            user = authenticate(username=username, password=password)

            if user and user.is_active:
                user.failed_attempts = 0 # Resetear intentos fallidos
                user.save()
                return user
            else:
                raise serializers.ValidationError("Credenciales invalidas")

        except:
            raise serializers.ValidationError("Usuario no encontrado")


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email')