from django.urls import path
from .views import (
    CreateMovieView,
    ListMovieView,
    UpdateMovieView,
    CreateHallView,
    UpdateHallView,
    CreateFunctionView,
    ListFunctionView,
    UpdateFunctionView
)

urlpatterns = [
    # Rutas para películas
    path('movies/create/', CreateMovieView.as_view(), name='create-movie'),
    path('movies/list/', ListMovieView.as_view(), name='list-movies'),
    path('movies/update/<int:pk>/', UpdateMovieView.as_view(), name='update-movie'),
    
    # Rutas para salas
    path('halls/create/', CreateHallView.as_view(), name='create-hall'),
    path('halls/update/<int:pk>/', UpdateHallView.as_view(), name='update-hall'),
    
    # Rutas para funciones
    path('functions/create/', CreateFunctionView.as_view(), name='create-function'),
    path('functions/list/', ListFunctionView.as_view(), name='list-functions'),
    path('functions/update/<int:pk>/', UpdateFunctionView.as_view(), name='update-function'),
]
