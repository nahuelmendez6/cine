from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAdminGroupUser
from .models import Movie, Hall, Function
from .serializers import MovieSerializer, HallSerializer, FunctionSerializer

# Create your views here.
class MovieViewSet(viewsets.ViewSet):


    """
    - Cargar películas x
    - Editar películas x
    - Crear funciones
    - Editar funciones
    - Listar películas x
    - Listar funciones
    """

    permission_classes = [AllowAny] # Los permisos de acceso se sobreescriben dependiendo de la funcionalidad


    @action(detail=False, methods=['post'], url_path='add/', permission_classes=[IsAuthenticated, IsAdminGroupUser])
    def add_new_movie(self, request):

        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            # Si el serializador es valido se crea un objeto Movie con los datos enviados en el request
            movie = serializer.save()
            return Response({'message':'Película agregada correctamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='view/')
    def view_movie_list(self, request):
        """ Listar todas las películas """
        movies = Movie.objects.all()
        if not movies.exists():
            return Response({'message':'No hay películas registradas'}, status=status.HTTP_204_NO_CONTENT)

        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['put'], url_path='update/')
    def update_movie(self, request, pk=None):
        """ Actualizar una película existente """
        movie = get_object_or_404(Movie, pk=pk)
        serializer = MovieSerializer(Movie, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Película actualizada existosamente'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)