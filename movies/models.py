from django.db import models

# Create your models here.
class Movie(models.Model):

    """
    Esta clase representa a cada pelicula
    """

    title = models.CharField(max_length=255)
    poster = models.ImageField(upload_to="posters/")
    synopsis = models.TextField()
    duration = models.IntegerField()
    genre = models.CharField(max_length=100)
    classification = models.CharField(max_length=50)
    trailer_url = models.URLField(blank=True, null=True)
    date_release = models.DateField()
    date_finish = models.DateField()
    available = models.BooleanField(default=True)

class Hall(models.Model):

    """
    Esta clase representa a cada sala dentro del cine
    """

    name = models.CharField(max_length=50)
    total_seats = models.IntegerField()
    available = models.BooleanField(default=True)

class Function(models.Model):

    """
    Esta clase representa a cada funcion
    """

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    function_date = models.DateField()
    function_time = models.TimeField()
    language = models.CharField(max_length=50, choices=[('subtitulada', 'Subtitulada'), ('doblada', 'Doblada')])
    format = models.CharField(max_length=50, choices=[('2D', '2D'), ('3D', '3D'), ('IMAX', 'IMAX')])
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)


