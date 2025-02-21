
from xmlrpc.client import Fault
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from movies.models import Function
from .models import Seat, Ticket, Combo, ComboTicket, Booking
from .serializers import BookingSerializer, SeatSerializer, TicketSerializer, ComboSerializer, ComboTicketSerializer
from .services import check_seat_availability, generate_ticket_code

# Create your views here.
class BookingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    """
    - crear reserva
    - seleccionar asientos
    - agregar combos a la reserva
    - listar reservas de un usuario
    - cancelar reservas
    """

    @action(detail=False, methods=['post'], url_path='create')
    def create_booking(self, request):
        """ crear una nueva reserva """

        serializer = BookingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            booking = serializer.save(user=request.user)
            return Response({'message':'Reserva creada correctamente', 'booking_id':booking.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'], url_path='select-seats')
    def select_seats(self, request):
        """ Seleccionar asientos para una reserva
            Recibe los asientos seleccionados, evalua su disponibilidad
            y crea los tickets correspondientes
        """

        booking_id = request.data.get('booking_id')
        seat_ids = request.data.get('seats', [])

        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        if not seat_ids:
            return Response({'message':'No se enviarion asientos'}, status=status.HTTP_400_BAD_REQUEST)

        tickets = []
        for seat_id in seat_ids:
            seat = get_object_or_404(Seat, id=seat_id)

            if not check_seat_availability(seat, booking.function):

                """ Si el asiento esta disponible se debe generar el ticket correspondiente"""

                ticket_code = generate_ticket_code(request.user, seat, booking.function)

                ticket = Ticket.objects.create(booking=booking, seat=seat, ticket_code=ticket_code)
                tickets.append(ticket)

                seat.seat_available = False
                seat.save()

        serializer = TicketSerializer(tickets, many=True)


    @action(detail=False, methods=['post'], url_path='add-combo')
    def add_combo(self, request):

        """ Agregar combo a reserva """

        booking_id = request.data.get('booking_id')
        combo_id = request.data.get('combo_id')
        quantity = request.data.get('quantity', 1)

        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        combo = get_object_or_404(Combo, id=combo_id)

        total_price = quantity * combo.combo_price

        combo_ticket = ComboTicket.objects.create(
            booking=booking,
            combo=combo,
            quantity=quantity,
            total_combo_price=total_price,
            combo_ticket_code=f"CMB-{combo_id}-{booking.id}"
        )

        serializer = ComboTicketSerializer(combo_ticket)
        return Response({'message':'Combo agregado correctamente', 'combo_ticker':combo_ticket}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='my-bookings')
    def my_bookings(self, request):
        """ Listar las reservas del usuario autenticado"""

        bookings = Booking.objects.filter(user=request.user)
        if not bookings.exists():
            return Response({'message': 'No tienes reservas registradas'}, status=status.HTTP_204_NO_CONTENT)

        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path='cancel')
    def cancel_booking(self, request, pk=None):
        """ Cancelar una reserva y liberar asientos """

        booking = get_object_or_404(Booking, id=pk, user=request.user)

        tickets = Ticket.objets.filter(booking=booking)
        for ticket in tickets:
            ticket.seat.seat_available = True
            ticket.seat.save()

        booking.status = 'cancelled'
        booking.save()

        return Response({'message': 'Reserva cancelada correctamente'}, status=status.HTTP_200_OK)
