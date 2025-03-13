"""
Este módulo contiene las vistas de la aplicación de cine.

Define las vistas para la gestión de:
- Películas (Movie): Creación, listado y actualización
- Salas (Hall): Creación y actualización
- Funciones (Function): Creación, listado y actualización

Cada vista está implementada como una APIView independiente, lo que permite:
- Control granular de permisos por operación
- URLs explícitas y descriptivas
- Separación clara de responsabilidades
- Documentación específica por endpoint
"""

from xmlrpc.client import Fault
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAdminGroupUser
from .models import Movie, Hall, Function
from .serializers import MovieSerializer, HallSerializer, FunctionSerializer

# Create your views here.
class CreateMovieView(APIView):
    """
    View para crear una nueva película.
    
    Permite crear una nueva película con los datos proporcionados en la solicitud.
    
    Requires authentication and admin group user permissions.
    Creates a new movie instance for the authenticated admin user.

    Methods:
        post: Crea una nueva instancia de película
    """ 
    permission_classes = [IsAuthenticated, IsAdminGroupUser]

    def post(self, request):
        """
        Creates a new movie instance for the authenticated admin user.

        Args:
            request: HTTP request containing movie data in request.data

        Returns:
            Response: 
                - 201 Created: Si la película se crea correctamente
                - 400 Bad Request: Si hay errores de validación
        """
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Película agregada correctamente',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListMovieView(APIView):
    """
    View para listar películas.
    
    Permite obtener la lista de todas las películas con opción de búsqueda.
    No requiere autenticación.

    Methods:
        get: Retorna la lista de películas con opción de búsqueda
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Retorna la lista de películas con opción de búsqueda.

        Args:
            request: HTTP request que puede contener parámetros de búsqueda

        Returns:
            Response:
                - 200 OK: Lista de películas
                - 204 No Content: Si no hay películas registradas
        """
        queryset = Movie.objects.all()
        
        # Agregar capacidad de búsqueda
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(synopsis__icontains=search)
            )

        if not queryset.exists():
            return Response(
                {'message': 'No hay películas registradas'}, 
                status=status.HTTP_204_NO_CONTENT
            )

        serializer = MovieSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateMovieView(APIView):
    """
    View para actualizar una película existente.
    
    Permite modificar los datos de una película específica.
    
    Requires authentication and admin group user permissions.

    Methods:
        put: Actualiza una película existente
    """
    permission_classes = [IsAuthenticated, IsAdminGroupUser]

    def put(self, request, pk):
        """
        Actualiza una película existente.
        
        Args:
            request: HTTP request con los datos a actualizar
            pk: ID de la película a actualizar

        Returns:
            Response:
                - 200 OK: Si la actualización es exitosa
                - 400 Bad Request: Si hay errores de validación
                - 404 Not Found: Si la película no existe
        """
        movie = get_object_or_404(Movie, pk=pk)
        serializer = MovieSerializer(movie, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Película actualizada exitosamente',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateHallView(APIView):
    """
    View para crear una nueva sala.
    
    Permite crear una nueva sala de proyección.
    
    Requires authentication and admin group user permissions.

    Methods:
        post: Crea una nueva instancia de sala
    """
    permission_classes = [IsAuthenticated, IsAdminGroupUser]

    def post(self, request):
        """
        Creates a new hall instance.

        Args:
            request: HTTP request containing hall data in request.data

        Returns:
            Response:
                - 201 Created: Si la sala se crea correctamente
                - 400 Bad Request: Si hay errores de validación
        """
        serializer = HallSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Sala agregada correctamente',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateHallView(APIView):
    """
    View para actualizar una sala existente.
    
    Permite modificar los datos de una sala específica.
    
    Requires authentication and admin group user permissions.

    Methods:
        put: Actualiza una sala existente
    """
    permission_classes = [IsAuthenticated, IsAdminGroupUser]

    def put(self, request, pk):
        """
        Actualiza una sala existente.
        
        Args:
            request: HTTP request con los datos a actualizar
            pk: ID de la sala a actualizar

        Returns:
            Response:
                - 200 OK: Si la actualización es exitosa
                - 400 Bad Request: Si hay errores de validación
                - 404 Not Found: Si la sala no existe
        """
        hall = get_object_or_404(Hall, pk=pk)
        serializer = HallSerializer(hall, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Sala actualizada exitosamente',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateFunctionView(APIView):
    """ 
    View para crear una nueva función.
    
    Permite crear una nueva función de proyección.
    
    Requires authentication and admin group user permissions.

    Methods:
        post: Crea una nueva instancia de función
    """
    permission_classes = [IsAuthenticated, IsAdminGroupUser]

    def post(self, request):
        """
        Creates a new function instance.

        Args:
            request: HTTP request containing function data in request.data

        Returns:
            Response:
                - 201 Created: Si la función se crea correctamente
                - 400 Bad Request: Si hay errores de validación
        """
        serializer = FunctionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Función agregada correctamente',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ListFunctionView(APIView):
    """
    View para listar funciones.
    
    Permite obtener la lista de todas las funciones con opciones de filtrado.
    No requiere autenticación.

    Methods:
        get: Retorna la lista de funciones con opciones de filtrado
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Retorna la lista de funciones con opciones de filtrado.

        Args:
            request: HTTP request que puede contener parámetros de filtrado:
                - movie_id: ID de la película para filtrar
                - date: Fecha para filtrar

        Returns:
            Response:
                - 200 OK: Lista de funciones
                - 204 No Content: Si no hay funciones registradas
        """
        queryset = Function.objects.all()
        
        # Filtrar por pelicula        
        movie_id = request.query_params.get('movie_id')
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)

        # Filtrar por fecha
        date = request.query_params.get('date')
        if date:
            queryset = queryset.filter(date=date)

        if not queryset.exists():
            return Response(
                {'message': 'No hay funciones registradas'},
                status=status.HTTP_204_NO_CONTENT
            )
        
        serializer = FunctionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UpdateFunctionView(APIView):
    """
    View para actualizar una función existente.
    
    Permite modificar los datos de una función específica.
    
    Requires authentication and admin group user permissions.

    Methods:
        put: Actualiza una función existente
    """
    permission_classes = [IsAuthenticated, IsAdminGroupUser]

    def put(self, request, pk):
        """
        Actualiza una función existente.
        
        Args:
            request: HTTP request con los datos a actualizar
            pk: ID de la función a actualizar

        Returns:
            Response:
                - 200 OK: Si la actualización es exitosa
                - 400 Bad Request: Si hay errores de validación
                - 404 Not Found: Si la función no existe
        """
        function = get_object_or_404(Function, pk=pk)
        serializer = FunctionSerializer(function, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Función actualizada exitosamente',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
