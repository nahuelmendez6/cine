"""
Este módulo contiene los serializadores de la aplicación de cine.

Define los serializadores para:
- HallSerializer: Maneja la serialización de salas de proyección
- MovieSerializer: Maneja la serialización de películas
- FunctionSerializer: Maneja la serialización de funciones de proyección

Cada serializador incluye validaciones específicas y métodos para crear y actualizar instancias.
"""

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from .models import Movie, Hall, Function
from .services import check_movie_upload, check_function_upload


class HallSerializer(serializers.Serializer):
    """
    Serializador para el modelo Hall.

    Maneja la serialización y deserialización de datos de salas de proyección,
    incluyendo validaciones específicas para nombres duplicados y número de asientos.

    Attributes:
        id (IntegerField): Identificador único de la sala (solo lectura)
        name (CharField): Nombre identificador de la sala
        total_seats (IntegerField): Número total de asientos
        available (BooleanField): Estado de disponibilidad de la sala
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    total_seats = serializers.IntegerField()
    available = serializers.BooleanField(default=True)

    def validate(self, data):
        """
        Valida los datos de la sala antes de la serialización.

        Args:
            data (dict): Diccionario con los datos a validar

        Returns:
            dict: Datos validados

        Raises:
            ValidationError: Si el nombre de la sala ya existe o el número de asientos es inválido
        """
        if Hall.objects.filter(name=data['name']).exists():
            raise serializers.ValidationError("El nombre de la sala ya existe")
        
        if data['total_seats'] <= 0:
            raise serializers.ValidationError("El numero de asientos debe ser mayor que 0")
        
        return data
    

    def create(self, validated_data):
        """
        Crea una nueva instancia de Hall.

        Args:
            validated_data (dict): Datos validados para crear la sala

        Returns:
            Hall: Nueva instancia de sala creada
        """
        hall = Hall.objects.create(**validated_data)
        return hall


    def update(self, instance, validated_data):
        """
        Actualiza una instancia existente de Hall.

        Args:
            instance (Hall): Instancia de sala a actualizar
            validated_data (dict): Nuevos datos validados

        Returns:
            Hall: Instancia de sala actualizada
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MovieSerializer(serializers.Serializer):  
    """
    Serializador para el modelo Movie.

    Maneja la serialización y deserialización de datos de películas,
    incluyendo validaciones para títulos duplicados y fechas de exhibición.

    Attributes:
        id (IntegerField): Identificador único de la película (solo lectura)
        title (CharField): Título de la película
        poster (ImageField): Imagen de portada
        synopsis (CharField): Descripción de la película
        duration (IntegerField): Duración en minutos
        genre (ChoiceField): Género de la película (opciones predefinidas)
        classification (CharField): Clasificación por edad
        trailer_url (URLField): Enlace al trailer
        date_release (DateField): Fecha de inicio de exhibición
        date_finish (DateField): Fecha de fin de exhibición
        available (BooleanField): Estado de disponibilidad
    """

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    poster = serializers.ImageField()
    synopsis = serializers.CharField()
    duration = serializers.IntegerField()
    genre = serializers.ChoiceField(choices=Movie.GENRE_CHOICES)
    classification = serializers.CharField(max_length=50)
    trailer_url = serializers.URLField()
    date_release = serializers.DateField()
    date_finish = serializers.DateField()
    available = serializers.BooleanField(default=True)

    def validate(self, data):
        """
        Valida los datos de la película antes de la serialización.

        Args:
            data (dict): Diccionario con los datos a validar

        Returns:
            dict: Datos validados

        Raises:
            ValidationError: Si el título ya existe o las fechas son inválidas
        """
        if Movie.objects.filter(title=data['title']).exists():
            raise serializers.ValidationError("Esta pelicula ya existe")
        
        if data['date_release'] > data['date_finish']:
            raise serializers.ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio")
        
        return data
    

    def create(self, validated_data):
        """
        Crea una nueva instancia de Movie.

        Args:
            validated_data (dict): Datos validados para crear la película

        Returns:
            Movie: Nueva instancia de película creada
        """
        movie = Movie.objects.create(**validated_data)
        return movie
    

    def update(self, instance, validated_data):
        """
        Actualiza una instancia existente de Movie.

        Args:
            instance (Movie): Instancia de película a actualizar
            validated_data (dict): Nuevos datos validados

        Returns:
            Movie: Instancia de película actualizada
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance 


class FunctionSerializer(serializers.Serializer):
    """
    Serializador para el modelo Function.

    Maneja la serialización y deserialización de datos de funciones de proyección,
    incluyendo validaciones para evitar duplicados y verificar la existencia de películas y salas.

    Attributes:
        movie (PrimaryKeyRelatedField): Relación con la película
        hall (PrimaryKeyRelatedField): Relación con la sala
        function_date (DateField): Fecha de la función
        function_time_start (TimeField): Hora de inicio
        function_time_end (TimeField): Hora de fin
        price (DecimalField): Precio de la entrada
        language (ChoiceField): Idioma de la proyección
        format (ChoiceField): Formato de proyección
    """

    movie = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all())
    hall = serializers.PrimaryKeyRelatedField(queryset=Hall.objects.all())
    function_date = serializers.DateField()
    function_time_start = serializers.TimeField()
    function_time_end = serializers.TimeField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)   
    language = serializers.ChoiceField(choices=Function.LANGUAGE_CHOICES)
    format = serializers.ChoiceField(choices=Function.FORMAT_CHOICES)   

    def validate(self, data):
        """
        Valida los datos de la función antes de la serialización.

        Args:
            data (dict): Diccionario con los datos a validar

        Returns:
            dict: Datos validados

        Raises:
            ValidationError: Si la película o sala no existen, o si la función ya existe
        """
        if not Movie.objects.filter(id=data['movie']).exists():
            raise serializers.ValidationError("La pelicula no existe")
        
        if not Hall.objects.filter(id=data['hall']).exists():
            raise serializers.ValidationError("La sala no existe")
        
        if Function.objects.filter(movie=data['movie'], hall=data['hall'], function_date=data['function_date'], function_time_start=data['function_time_start']).exists():
            raise serializers.ValidationError("Esta funcion ya existe")
        
        return data
    
    def create(self, validated_data):
        """
        Crea una nueva instancia de Function.

        Args:
            validated_data (dict): Datos validados para crear la función

        Returns:
            Function: Nueva instancia de función creada
        """
        function = Function.objects.create(**validated_data)
        return function
    
    def update(self, instance, validated_data):
        """
        Actualiza una instancia existente de Function.

        Args:
            instance (Function): Instancia de función a actualizar
            validated_data (dict): Nuevos datos validados

        Returns:
            Function: Instancia de función actualizada
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance 
    
    
    
    
    