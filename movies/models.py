"""
Este módulo contiene los modelos principales de la aplicación de cine.

Define las estructuras de datos para:
- Películas (Movie): Información detallada de cada película
- Salas (Hall): Características de las salas de proyección
- Funciones (Function): Programación de proyecciones de películas
"""

import datetime

from django.db import models

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
        poster (ImageField): Imagen de portada de la película
        synopsis (TextField): Descripción detallada de la película
        duration (IntegerField): Duración en minutos
        genre (CharField): Género de la película (seleccionable de GENRE_CHOICES)
        classification (CharField): Clasificación por edad (ej: +18, R)
        trailer_url (URLField): Enlace al trailer de la película
        date_release (DateField): Fecha de inicio de exhibición
        date_finish (DateField): Fecha de fin de exhibición
        available (BooleanField): Estado de disponibilidad de la película
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
    poster = models.ImageField(upload_to="posters/", null=True)    # posters/fotos de portada
    synopsis = models.TextField()                       # breve texto descriptivo
    duration = models.IntegerField()                    # duracion en minutos
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)            # genero (accion, comedia, animacion...)
    classification = models.CharField(max_length=50, null=True)    # sistema de clasificacion (+18, R)
    trailer_url = models.URLField(blank=True, null=True)    # Enlace a trailer
    date_release = models.DateField()                   # a partir de esta fecha la pelicula se mostrara al cliente
    date_finish = models.DateField()                    # a partir de esta fecha la pelicula se oculta al cliente
    available = models.BooleanField(default=True)

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


