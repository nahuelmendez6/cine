from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Seat, Ticket, Combo, ComboTicket, Booking
from .services import (generate_ticket_code, check_seat_availability, validate_ticket_purchase, check_seat_availability,
                       release_expired_reservations, generate_qr_code, send_confirmation_email)


class SeatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Seat
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = '__all__'


class ComboSerializer(serializers.ModelSerializer):

    class Meta:
        model = Combo
        fields = '__all__'


class ComboTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = ComboTicket
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = '__all__'