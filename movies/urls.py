from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CreateMovieView,
    ListMovieView,
    UpdateMovieView,
    CreateHallView,
    UpdateHallView,
    FunctionViewSet
)

router = DefaultRouter()
router.register(r'functions', FunctionViewSet, basename='functions')

urlpatterns = [
    # Rutas para películas
    path('movies/create/', CreateMovieView.as_view(), name='create-movie'),
    path('movies/list/', ListMovieView.as_view(), name='list-movies'),
    path('movies/update/<int:pk>/', UpdateMovieView.as_view(), name='update-movie'),
    
    # Rutas para salas
    path('halls/create/', CreateHallView.as_view(), name='create-hall'),
    path('halls/update/<int:pk>/', UpdateHallView.as_view(), name='update-hall'),
    
    # Rutas para funciones (mantenemos el router para el ViewSet)
    path('', include(router.urls))
]
