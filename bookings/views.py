"""
Views for handling cinema booking operations including creating bookings,
selecting seats, adding combos, viewing bookings and cancelling them.
"""

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
    """
    View for creating new bookings.
    
    Requires authentication.
    Creates a new booking instance for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Creates a new booking for a movie function.
        
        Args:
            request: HTTP request containing booking details in request.data
        
        Returns:
            Response with booking_id if successful, errors otherwise
        """
        serializer = BookingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            booking = serializer.save(user=request.user)
            return Response({
                'message': 'Reserva creada correctamente',
                'booking_id': booking.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SelectSeatsView(APIView):
    """
    View for handling seat selection for a booking.
    
    Requires authentication.
    Handles the process of selecting and reserving seats for a booking,
    including validation, ticket generation, and notification.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Process seat selection for a booking.
        
        Args:
            request: HTTP request containing booking_id and list of seat_ids
        
        Returns:
            Response with created tickets if successful, error message otherwise
        
        Workflow:
        1. Validates seat availability
        2. Checks purchase limits
        3. Creates tickets
        4. Generates QR codes
        5. Sends confirmation emails
        """
        # Extract booking and seat information from request
        booking_id = request.data.get('booking_id')
        seat_ids = request.data.get('seats', [])

        # Get the booking or return 404 if not found
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        if not seat_ids:
            return Response({'message': 'No se enviaron asientos'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate against maximum ticket purchase limit
            validate_ticket_purchase(request.user, seat_ids, booking.function)
            
            tickets = []
            for seat_id in seat_ids:
                # Get and validate each seat
                seat = get_object_or_404(Seat, id=seat_id)
                
                # Verify seat is available for this function
                check_seat_availability(seat, booking.function)
                
                # Generate unique ticket identifier
                ticket_code = generate_ticket_code(request.user, seat, booking.function)
                
                # Create ticket record in database
                ticket = Ticket.objects.create(
                    booking=booking,
                    seat=seat,
                    ticket_code=ticket_code
                )
                
                # Update seat availability status
                seat.seat_available = False
                seat.save()
                
                # Generate QR code and send confirmation
                qr_code_path = generate_qr_code(ticket)
                send_confirmation_email(ticket, qr_code_path)
                
                tickets.append(ticket)

            # Serialize and return created tickets
            serializer = TicketSerializer(tickets, many=True)
            return Response({
                'message': 'Asientos seleccionados correctamente',
                'tickets': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AddComboView(APIView):
    """
    View for adding food and beverage combos to a booking.
    
    Requires authentication.
    Allows users to add combo items to their existing booking.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Add a combo to an existing booking.
        
        Args:
            request: HTTP request containing booking_id, combo_id and quantity
        
        Returns:
            Response with created combo ticket if successful
        """
        booking_id = request.data.get('booking_id')
        combo_id = request.data.get('combo_id')
        quantity = request.data.get('quantity', 1)

        # Validate booking and combo exist
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        combo = get_object_or_404(Combo, id=combo_id)

        # Calculate total price for the combo order
        total_price = quantity * combo.combo_price

        # Create combo ticket record
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
    """
    View for retrieving user's bookings.
    
    Requires authentication.
    Returns all bookings associated with the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all bookings for the authenticated user.
        
        Returns:
            Response with list of bookings or no content message if none exist
        """
        bookings = Booking.objects.filter(user=request.user)
        if not bookings.exists():
            return Response({
                'message': 'No tienes reservas registradas'
            }, status=status.HTTP_204_NO_CONTENT)

        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CancelBookingView(APIView):
    """
    View for cancelling bookings.
    
    Requires authentication.
    Handles the cancellation process including releasing reserved seats.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, booking_id):
        """
        Cancel a booking and release associated seats.
        
        Args:
            request: HTTP request
            booking_id: ID of the booking to cancel
        
        Returns:
            Response confirming cancellation
        """
        # Verify booking exists and belongs to user
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        # Release all seats associated with the booking
        tickets = Ticket.objects.filter(booking=booking)
        for ticket in tickets:
            ticket.seat.seat_available = True
            ticket.seat.save()

        # Mark booking as cancelled
        booking.status = 'cancelled'
        booking.save()

        return Response({
            'message': 'Reserva cancelada correctamente'
        }, status=status.HTTP_200_OK)
