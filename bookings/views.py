from xmlrpc.client import Fault
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from movies.models import Function
from .models import Seat, Ticket, Combo, ComboTicket, Booking
from .serializers import BookingSerializer, SeatSerializer, TicketSerializer, ComboSerializer, ComboTicketSerializer
from .services import (
    check_seat_availability, 
    generate_ticket_code, 
    validate_ticket_purchase,
    generate_qr_code,
    send_confirmation_email
)

# Create your views here.
class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            booking = serializer.save(user=request.user)
            return Response({
                'message': 'Reserva creada correctamente',
                'booking_id': booking.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SelectSeatsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        seat_ids = request.data.get('seats', [])

        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        if not seat_ids:
            return Response({'message': 'No se enviaron asientos'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate ticket purchase limits
            validate_ticket_purchase(request.user, seat_ids, booking.function)
            
            tickets = []
            for seat_id in seat_ids:
                seat = get_object_or_404(Seat, id=seat_id)
                
                # Check seat availability using service
                check_seat_availability(seat, booking.function)
                
                # Generate ticket code using service
                ticket_code = generate_ticket_code(request.user, seat, booking.function)
                
                # Create ticket
                ticket = Ticket.objects.create(
                    booking=booking,
                    seat=seat,
                    ticket_code=ticket_code
                )
                
                # Mark seat as unavailable
                seat.seat_available = False
                seat.save()
                
                # Generate QR code and send confirmation email
                qr_code_path = generate_qr_code(ticket)
                send_confirmation_email(ticket, qr_code_path)
                
                tickets.append(ticket)

            serializer = TicketSerializer(tickets, many=True)
            return Response({
                'message': 'Asientos seleccionados correctamente',
                'tickets': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AddComboView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
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
        return Response({
            'message': 'Combo agregado correctamente',
            'combo_ticket': serializer.data
        }, status=status.HTTP_201_CREATED)

class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user)
        if not bookings.exists():
            return Response({
                'message': 'No tienes reservas registradas'
            }, status=status.HTTP_204_NO_CONTENT)

        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        tickets = Ticket.objects.filter(booking=booking)
        for ticket in tickets:
            ticket.seat.seat_available = True
            ticket.seat.save()

        booking.status = 'cancelled'
        booking.save()

        return Response({
            'message': 'Reserva cancelada correctamente'
        }, status=status.HTTP_200_OK)
