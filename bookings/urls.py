from django.urls import path
from .views import (
    CreateBookingView,
    SelectSeatsView,
    AddComboView,
    MyBookingsView,
    CancelBookingView
)

app_name = 'bookings'

urlpatterns = [
    # Crear una nueva reserva
    path('create/', CreateBookingView.as_view(), name='create-booking'),
    
    # Seleccionar asientos para una reserva
    path('select-seats/', SelectSeatsView.as_view(), name='select-seats'),
    
    # Agregar combo a una reserva
    path('add-combo/', AddComboView.as_view(), name='add-combo'),
    
    # Ver reservas del usuario
    path('my-bookings/', MyBookingsView.as_view(), name='my-bookings'),
    
    # Cancelar una reserva
    path('cancel/<int:booking_id>/', CancelBookingView.as_view(), name='cancel-booking'),
] 