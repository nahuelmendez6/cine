from django.db import models

# Create your models here.
class Movie(models.Model):

    """
    Esta clase representa a cada pelicula
    """

    title = models.CharField(max_length=255)            # titulo de la pelicula
    poster = models.ImageField(upload_to="posters/")    # posters/fotos de portada
    synopsis = models.TextField()                       # breve texto descriptivo
    duration = models.IntegerField()                    # duracion en minutos
    genre = models.CharField(max_length=100)            # genero (accion, comedia, animacion...)
    classification = models.CharField(max_length=50)    # sistema de clasificacion (+18, R)
    trailer_url = models.URLField(blank=True, null=True)    # Enlace a trailer
    date_release = models.DateField()                   # a partir de esta fecha la pelicula se mostrara al cliente
    date_finish = models.DateField()                    # a partir de esta fecha la pelicula se oculta al cliente
    available = models.BooleanField(default=True)

class Hall(models.Model):

    """
    Esta clase representa a cada sala dentro del cine
    """

    name = models.CharField(max_length=50)  # nombre de la sala (sala 1, sala 2, ...)
    total_seats = models.IntegerField()     # total de asientos disponibles
    available = models.BooleanField(default=True)   # la sala puede estar inhabilitada ciertos dias

class Function(models.Model):

    """
    Esta clase representa a cada funcion
    """

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)      # una pelicula tendra varias funciones
    function_date = models.DateField()
    function_time_start = models.TimeField()
    function_time_end = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    language = models.CharField(max_length=50, choices=[('subtitulada', 'Subtitulada'), ('doblada', 'Doblada')])
    format = models.CharField(max_length=50, choices=[('2D', '2D'), ('3D', '3D'), ('IMAX', 'IMAX')])
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)


