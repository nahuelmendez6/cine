from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthView

router = DefaultRouter()
router.register(r'auth', AuthView, basename='auth')

urlpatters = [
    path('', include(router.urls))
]
