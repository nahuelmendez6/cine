from xmlrpc.client import Fault

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


    @action(detail=False, methods=['post'], url_path='add', permission_classes=[IsAuthenticated, IsAdminGroupUser])
    def add_new_movie(self, request):

        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            # Si el serializador es valido se crea un objeto Movie con los datos enviados en el request
            movie = serializer.save()
            return Response({'message':'Película agregada correctamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='view')
    def view_movie_list(self, request):
        """ Listar todas las películas """
        movies = Movie.objects.all()
        if not movies.exists():
            return Response({'message':'No hay películas registradas'}, status=status.HTTP_204_NO_CONTENT)

        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['put'], url_path='update')
    def update_movie(self, request, pk=None):
        """ Actualizar una película existente """
        movie = get_object_or_404(Movie, pk=pk)
        serializer = MovieSerializer(Movie, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Película actualizada existosamente'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    """  Hall endpoints    """

    @action(detail=False, methods=['post'], url_path='add/hall', permission_classes=[IsAuthenticated, IsAdminGroupUser])
    def add_new_hall(self, request):

        serializer = HallSerializer(data=request.data)
        if serializer.is_valid():
            hall = serializer.save()
            return Response({'message': 'Sala agregaa correctamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], url_path='update/hall')
    def update_hall(self, request, pk=None):

        hall = get_object_or_404(Hall, pk)
        serializer = HallSerializer(Hall, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Sala actualizada existosamente'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    """  Functions endpoints """

class FunctionViewSet(viewsets.ViewSet):

    """
    - Agregar funcion
    - Listar funciones
    - Editar funcion
    - Eliminar funcion
    """

    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='add/function')
    def add_function(self, request):

        serializer = FunctionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Función agregada correctamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'], url_path='view/functions')
    def view_functions(self, request):
        """ Listar todas las funciones """
        functions = Function.objects.all()
        if not functions.exists():
            return Response({'message':'No hay funciones registradas'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FunctionSerializer(functions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'], url_path='update/function')
    def update_function(self, request, pk=None):
        function = get_object_or_404(Function, pk=pk)
        serializer = FunctionSerializer(function, data=request.data, partial=True)

        if serializer.is_valid():
            return Response({'message':'Función actualizada correctamente'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path='delete/function')
    def delete_function(self, request, pk=None):
        function = get_object_or_404(Function, pk=pk)
        function.delete()
        return Response({'message':'Funcion eliminada correctamente'}, status=status.HTTP_200_OK)