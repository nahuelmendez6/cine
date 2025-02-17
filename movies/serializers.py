from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from .models import Movie, Hall, Function
from .services import check_movie_upload, check_function_upload

class HallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

    def validate_title(self, value):
        """ Validar que no se cargue la misma película mas de una vez """
        check_movie_upload(value)
        return value

class FunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Function
        fields = '__all__'

    def validate(self, data):

        """
        Verificar que la función no se duplique y evitar solapamientos en la misma
        """
        check_function_upload(
            movie=data['movie'],
            function=data.get('function'),
            hall=data['hall'],
            function_date=data['function_date'],
            function_time_start=data['function_time_start'],
            function_time_end=data['function_time_end'],
            language=data['language'],
            format=data['format']
        )

        return data


