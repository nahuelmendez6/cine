from datetime import timedelta
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied


from .models import CustomUser

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text="Requerido. 150 caracteres o menos."
    )
    email = serializers.EmailField(
        required=True,
        help_text="Requerido. Ingrese un email válido."
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        help_text="La contraseña debe tener al menos 8 caracteres."
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Repita la contraseña para verificación."
    )
    is_admin = serializers.BooleanField(
        default=False,
        required=False
    )
    is_customer = serializers.BooleanField(
        default=True,
        required=False
    )

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden."
            })
        return data

    def create(self, validated_data):
        # Removemos password2 ya que no es parte del modelo
        validated_data.pop('password2')
        
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_admin=validated_data.get('is_admin', False),
            is_customer=validated_data.get('is_customer', True)
        )
        return user

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'is_admin': instance.is_admin,
            'is_customer': instance.is_customer
        }

    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        try:
            user = CustomUser.objects.get(username=username)

            if user.is_locked:
                user.unlock()
                if user.is_locked:
                    raise serializers.ValidationError({
                        'error':"Usuario bloqueado.",
                        'locked_until': user.lockout_time + timedelta(minutes=10)
                    })
            
            if not user.check_password(password):
                user.increment_failed_attempts()
                raise serializers.ValidationError({
                    'error':'Contraseña incorrecta.',
                    'attempts_left': 3 - user.failed_attempts
                })
            
            if not user.is_active:
                raise serializers.ValidationError('Tu cuenta está desactivada.')
            
            # Reset intentos fallidos si la autenticacion es exitosa
            user.reset_failed_attempts()
            return {
                'user': user,
                'username': username
            }
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")
        
        

    