import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cine.settings')  # Asegúrate de que 'cine_app' sea el nombre correcto de tu proyecto
django.setup()

from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Movie, Hall, Function
import datetime
# Create your tests here.

class MovieTestCase(TestCase):
    def setUp(self):
        # Crear una pelicula para usar en los tests
        self.movie = Movie.objects.create(
            title="Inception",
            poster="posters/inception.jpg",
            synopsis="A mind-bending thriller",
            duration=148,
            genre="Sci-Fi",
            classification="PG-13",
            trailer_url="https://www.youtube.com/watch?v=YoHD9XEInc0",
            date_release=datetime.date(2024, 5, 1),
            date_finish=datetime.date(2024, 6, 1)
        )

    def test_duplicate_movie_upload(self):
        # Intentar subir una pelicula con el mismo titulo debería lanzar un ValidationError
        from .services import check_movie_upload
        with self.assertRaises(ValidationError):
            check_movie_upload("Inception")


class FunctionTestCase(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Interstellar",
            poster="posters/interstellar.jpg",
            synopsis="Exploración espacial para salvar la humanidad",
            duration=169,
            genre="Sci-Fi",
            classification="PG-13",
            trailer_url="https://www.youtube.com/watch?v=zSWdZVtXT7E",
            date_release=datetime.date(2024, 5, 15),
            date_finish=datetime.date(2024, 7, 15)
        )

        self.hall = Hall.objects.create(
            name="Sala 1",
            total_seats=100
        )

        # Crear una función inicial
        self.function = Function.objects.create(
            movie=self.movie,
            hall=self.hall,
            function_date=datetime.date(2024, 5, 20),
            function_time_start=datetime.time(18, 0),
            function_time_end=datetime.time(20, 30),
            price=10.00,
            language='subtitulada',
            format='2D'
        )

    def test_duplicate_function_upload(self):
        # Intentar cargar una función idéntica debería lanzar un ValidationError
        from .services import check_function_upload
        with self.assertRaises(ValidationError):
            check_function_upload(
                movie=self.movie,
                hall=self.hall,
                function_date=datetime.date(2024, 5, 20),
                function_time_start=datetime.time(18, 0),
                function_time_end=datetime.time(20, 30),
                language='subtitulada',
                format='2D'
            )

    def test_overlapping_function(self):
        # Crear una función con horarios que se solapan con la función existente
        from .services import check_function_upload
        with self.assertRaises(ValidationError):
            check_function_upload(
                movie=self.movie,
                hall=self.hall,
                function_date=datetime.date(2024, 5, 20),
                function_time_start=datetime.time(19, 0),  # Empieza antes de que termine la primera función
                function_time_end=datetime.time(21, 0),
                language='subtitulada',
                format='2D'
            )

    class FunctionModelValidationTestCase(TestCase):
        def setUp(self):
            self.movie = Movie.objects.create(
                title="The Dark Knight",
                poster="posters/dark_knight.jpg",
                synopsis="Batman enfrenta al Joker en Gotham",
                duration=152,
                genre="Action",
                classification="PG-13",
                date_release=datetime.date(2024, 4, 10),
                date_finish=datetime.date(2024, 5, 20)
            )
            self.hall = Hall.objects.create(name="Sala 2", total_seats=80)

        def test_function_time_validation(self):
            # Intentar crear una función con tiempo de fin anterior al de inicio
            function = Function(
                movie=self.movie,
                hall=self.hall,
                function_date=datetime.date(2024, 4, 15),
                function_time_start=datetime.time(20, 0),
                function_time_end=datetime.time(19, 0),  # Hora de fin inválida
                price=12.00,
                language='doblada',
                format='IMAX'
            )

            with self.assertRaises(ValidationError):
                function.full_clean()  # Esto ejecuta la validación personalizada en el modelo

