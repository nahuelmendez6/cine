from django.core.exceptions import ValidationError
from .models import Movie, Hall, Function

"""
No permitir cargar dos veces la misma película en la misma fecha y sala:
Asegura la correcta gestión de la cartelera.
"""

def check_movie_upload(title):
    if Movie.objects.filter(title=title).exists():
        raise ValidationError("Esta película ya ha sido cargada")

def check_hall_upload(name):
    if Hall.objects.filter(name=name).exists():
        raise ValidationError("Esta sala ya ha sido creada")


def check_function_upload(movie, function, hall, function_date, function_time_start, function_time_end,
                          language, format):
    if Function.objects.filter(movie=movie,
                              function=function,
                              hall=hall,
                              function_time_start=function_time_start,
                              function_date=function_date,
                              function_time_end=function_time_end,
                              language=language,
                              format=format
                              ).exists():
        raise ValidationError("Esta función ya se ha registrado en el sistema")

    """
    Verifiacion adicional: evitar solapamiento de funciones en la misma sala
    """

    overlapping_functions = Function.objects.filter(
        hall=hall,
        function_date=function_date,
        function_time_start=function_time_start,
        function_time_end=function_time_end
    )
    if overlapping_functions.exists():
        raise ValidationError("El horario de esta función se superpone con otra.")