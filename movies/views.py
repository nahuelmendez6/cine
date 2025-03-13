from xmlrpc.client import Fault
from django.db.models import Q
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
    ViewSet para la gestión de películas.
    
    Proporciona endpoints para:
    - Cargar películas
    - Editar películas
    - Listar películas
    """
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Define permisos específicos para cada acción"""
        if self.action in ['add_new_movie', 'update_movie', 'add_new_hall', 'update_hall']:
            return [IsAuthenticated(), IsAdminGroupUser()]
        return [AllowAny()]

    @action(detail=False, methods=['post'], url_path='add')
    def add_new_movie(self, request):
        """Agregar una nueva película"""
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Película agregada correctamente', 'data': serializer.data}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='view')
    def view_movie_list(self, request):
        """Listar todas las películas con opción de filtrado"""
        queryset = Movie.objects.all()
        
        # Agregar capacidad de búsqueda
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        if not queryset.exists():
            return Response(
                {'message': 'No hay películas registradas'}, 
                status=status.HTTP_204_NO_CONTENT
            )

        serializer = MovieSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], url_path='update')
    def update_movie(self, request, pk=None):
        """Actualizar una película existente"""
        movie = get_object_or_404(Movie, pk=pk)
        serializer = MovieSerializer(movie, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Película actualizada exitosamente',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='add/hall')
    def add_new_hall(self, request):
        """Agregar una nueva sala"""
        serializer = HallSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Sala agregada correctamente',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='update/hall')
    def update_hall(self, request, pk=None):
        """Actualizar una sala existente"""
        hall = get_object_or_404(Hall, pk=pk)
        serializer = HallSerializer(hall, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Sala actualizada exitosamente',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FunctionViewSet(viewsets.ViewSet):
    """
    ViewSet para la gestión de funciones.
    
    Proporciona endpoints para:
    - Agregar función
    - Listar funciones
    - Editar función
    - Eliminar función
    """
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Define permisos específicos para cada acción"""
        if self.action in ['add_function', 'update_function', 'delete_function']:
            return [IsAuthenticated(), IsAdminGroupUser()]
        return [AllowAny()]

    @action(detail=False, methods=['post'], url_path='add/function')
    def add_function(self, request):
        """Agregar una nueva función"""
        serializer = FunctionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Función agregada correctamente',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='view/functions')
    def view_functions(self, request):
        """Listar todas las funciones con opciones de filtrado"""
        queryset = Function.objects.all()
        
        # Filtrar por película
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

    @action(detail=True, methods=['put'], url_path='update/function')
    def update_function(self, request, pk=None):
        """Actualizar una función existente"""
        function = get_object_or_404(Function, pk=pk)
        serializer = FunctionSerializer(function, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Función actualizada correctamente',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='delete/function')
    def delete_function(self, request, pk=None):
        """Eliminar una función existente"""
        function = get_object_or_404(Function, pk=pk)
        function.delete()
        return Response(
            {'message': 'Función eliminada correctamente'},
            status=status.HTTP_200_OK
        )