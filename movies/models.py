"""
Este módulo contiene los modelos principales de la aplicación de cine.

Define las estructuras de datos para:
- Películas (Movie): Información detallada de cada película
- Salas (Hall): Características de las salas de proyección
- Funciones (Function): Programación de proyecciones de películas
"""

import datetime
from django.db import models
from django.utils.text import slugify
import logging

logger = logging.getLogger('cine')

# Create your models here.
class Movie(models.Model):
    """
    Modelo que representa una película en el sistema.

    Este modelo almacena toda la información relevante de una película,
    incluyendo sus características básicas, fechas de exhibición y estado de disponibilidad.

    Attributes:
        GENRE_CHOICES (list): Lista de tuplas que define los géneros disponibles para las películas.
            Cada tupla contiene (valor, etiqueta) donde:
            - valor: identificador interno del género
            - etiqueta: nombre legible del género

        title (CharField): Título de la película
        slug (SlugField): Campo para generar URLs amigables para la película
        description (TextField): Descripción detallada de la película
        duration (IntegerField): Duración en minutos
        release_date (DateField): Fecha de inicio de exhibición
        rating (DecimalField): Calificación de la película
        genre (CharField): Género de la película (seleccionable de GENRE_CHOICES)
        is_active (BooleanField): Estado de disponibilidad de la película
        created_at (DateTimeField): Fecha y hora de creación del registro
        updated_at (DateTimeField): Fecha y hora de última actualización del registro
    """

    GENRE_CHOICES = [
        ('accion', 'Acción'),
        ('aventura', 'Aventura'),
        ('animacion', 'Animación'),
        ('comedia', 'Comedia'),
        ('crimen', 'Crimen'),
        ('documental', 'Documental'),
        ('drama', 'Drama'),
        ('familia', 'Familia'),
        ('fantasia', 'Fantasía'),
        ('historia', 'Historia'),
        ('terror', 'Terror'),
        ('musica', 'Música'),
        ('misterio', 'Misterio'),
        ('romance', 'Romance'),
        ('ciencia_ficcion', 'Ciencia Ficción'),
        ('deportes', 'Deportes'),
        ('suspenso', 'Suspenso'),
        ('guerra', 'Guerra'),
        ('western', 'Western'),
    ]

    title = models.CharField(max_length=255)            # titulo de la pelicula
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()                       # breve texto descriptivo
    duration = models.IntegerField(help_text="Duration in minutes")                    # duracion en minutos
    release_date = models.DateField()                   # a partir de esta fecha la pelicula se mostrara al cliente
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)            # genero (accion, comedia, animacion...)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['release_date']),
            models.Index(fields=['genre']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['-release_date']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f'Error saving movie {self.title}: {str(e)}', exc_info=True)
            raise

    def __str__(self):
        """Retorna el título de la película como representación en string."""
        return self.title

class Hall(models.Model):
    """
    Modelo que representa una sala de proyección en el cine.

    Este modelo almacena la información básica de cada sala,
    incluyendo su capacidad y estado de disponibilidad.

    Attributes:
        name (CharField): Nombre identificador de la sala
        total_seats (IntegerField): Número total de asientos disponibles
        available (BooleanField): Estado de disponibilidad de la sala
    """

    name = models.CharField(max_length=50)  # nombre de la sala (sala 1, sala 2, ...)
    total_seats = models.IntegerField()     # total de asientos disponibles
    available = models.BooleanField(default=True)   # la sala puede estar inhabilitada ciertos dias

    def __str__(self):
        """Retorna el nombre de la sala como representación en string."""
        return self.name

class Function(models.Model):
    """
    Modelo que representa una función de proyección de película.

    Este modelo relaciona una película con una sala y especifica los detalles
    de la proyección, incluyendo fecha, hora, precio y características técnicas.

    Attributes:
        movie (ForeignKey): Relación con el modelo Movie
        function_date (DateField): Fecha de la función
        function_time_start (TimeField): Hora de inicio de la función
        function_time_end (TimeField): Hora de fin de la función
        price (DecimalField): Precio de la entrada
        language (CharField): Idioma de la proyección (subtitulada/doblada)
        format (CharField): Formato de proyección (2D/3D/IMAX)
        hall (ForeignKey): Relación con el modelo Hall
    """

    LANGUAGE_CHOICES = [
        ('subtitulada', 'Subtitulada'),
        ('doblada', 'Doblada'),
    ]

    FORMAT_CHOICES = [
        ('2D', '2D'),
        ('3D', '3D'),
        ('IMAX', 'IMAX'),
    ]

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)      # una pelicula tendra varias funciones
    function_date = models.DateField()
    function_time_start = models.TimeField(default=datetime.time)
    function_time_end = models.TimeField(default=datetime.time())
    price = models.DecimalField(max_digits=10, decimal_places=2)
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES)
    format = models.CharField(max_length=50, choices=FORMAT_CHOICES)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)

    def __str__(self):
        """Retorna una representación en string de la función."""
        return f"{self.movie.title} - {self.hall.name} - {self.function_date} {self.function_time_start}"


