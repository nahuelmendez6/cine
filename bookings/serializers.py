from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Seat, Ticket, Combo, ComboTicket, Booking
from movies.models import Hall
from movies.serializers import HallSerializer
from .services import (generate_ticket_code, check_seat_availability, validate_ticket_purchase,
                      release_expired_reservations, generate_qr_code, send_confirmation_email)
from users.models import CustomUser
from movies.models import Function


class SeatSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    hall = HallSerializer(read_only=True)
    row = serializers.IntegerField()
    number = serializers.IntegerField()  # ID de la sala
    seat_available = serializers.BooleanField()
    
    def validate(self, data):
        """
        Validación personalizada para asegurar que el asiento sea válido
        """
        try:
            hall = Hall.objects.get(id=data['hall'])
        except Hall.DoesNotExist:
            raise serializers.ValidationError({"hall": "La sala especificada no existe"})
        
        # Validar rangos según capacidad de la sala
        if data['row'] < 1 or data['row'] > hall.rows:
            raise serializers.ValidationError({
                "row": f"La fila debe estar entre 1 y {hall.rows}"
            })
        
        if data['number'] < 1 or data['number'] > hall.seats_per_row:
            raise serializers.ValidationError({
                "number": f"El número de asiento debe estar entre 1 y {hall.seats_per_row}"
            })
        
        # Verificar si el asiento ya existe
        if Seat.objects.filter(
            hall=hall,
            row=data['row'],
            number=data['number']
        ).exists():
            raise serializers.ValidationError({
                "seat": "Ya existe un asiento en esta posición"
            })
        
        return data
    
    def create(self, validated_data):
        """
        Crea un nuevo asiento con validaciones previas
        """
        # Establecer estado inicial por defecto si no se proporciona
        if 'status' not in validated_data:
            validated_data['status'] = 'available'
            
        # Crear el asiento
        seat = Seat.objects.create(**validated_data)
        return seat
        
    def update(self, instance, validated_data):
        """
        Actualiza un asiento existente con validaciones previas
        """
        # Validar que el asiento no esté reservado o ocupado antes de permitir cambios
        if instance.seat_available is False:
            raise serializers.ValidationError({
                "seat": "No se puede modificar un asiento que está reservado u ocupado"
            })
        
        # Si se actualiza el hall, row o number, verificar que no exista esa combinación
        if any(key in validated_data for key in ['hall', 'row', 'number']):
            # Usar los valores nuevos o los existentes para la validación
            hall = validated_data.get('hall', instance.hall)
            row = validated_data.get('row', instance.row)
            number = validated_data.get('number', instance.number)
            
            # Excluir la instancia actual de la búsqueda para evitar falsos positivos
            if Seat.objects.filter(
                hall=hall,
                row=row,
                number=number
            ).exclude(id=instance.id).exists():
                raise serializers.ValidationError({
                    "seat": "Ya existe un asiento en esta posición"
                })
        
        # Actualizar los campos del asiento
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Guardar los cambios
        instance.save()
        return instance

class BookingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    function = serializers.PrimaryKeyRelatedField(queryset=Function.objects.all())
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    status = serializers.ChoiceField(
        choices=[
            ('pending', 'Pendiente'),
            ('paid', 'Pagado'),
            ('cancelled', 'cancelado'),
            ('expired', 'Expirado')
        ]
    )
    
    def validate(self, data):
        """
        Validaciones a nivel de objeto:
        1. Verificar que el usuario exista
        2. Verificar que la función exista y esté disponible
        3. Validar que el estado inicial sea 'pending'
        """
        user = data.get('user')
        function = data.get('function')
        status = data.get('status')
        
        if not user or not function:
            raise serializers.ValidationError({
                "booking": "Se requiere tanto el usuario como la función"
            })
            
        # Validar que el estado inicial sea 'pending'
        if status and status != 'pending':
            raise serializers.ValidationError({
                "status": "El estado inicial debe ser 'pending'"
            })
            
        return data
    
    def create(self, validated_data):
        """
        Crea una nueva reserva con los datos validados.
        La lógica de negocio (cálculo de precio total, timeout, etc.) se maneja en las views.
        """
        # Crear la reserva con los datos validados
        booking = Booking.objects.create(**validated_data)
        return booking
    
    def update(self, instance, validated_data):
        """
        Actualiza una reserva existente con los datos validados.
        La lógica de negocio (recalculo de precio, notificaciones, etc.) se maneja en las views.
        """
        # Actualizar los campos de la reserva
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Guardar los cambios
        instance.save()
        return instance


class TicketSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    booking = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all())
    seat = serializers.PrimaryKeyRelatedField(queryset=Seat.objects.all())
    ticket_code = serializers.CharField(read_only=True)
    issued_at = serializers.DateTimeField(read_only=True)
    is_scanned = serializers.BooleanField(read_only=True)
    
    def validate(self, data):
        """
        Validaciones a nivel de objeto:
        1. Verificar que el asiento exista y esté disponible
        2. Validar que el booking exista y esté en estado válido
        3. Verificar que el asiento pertenezca a la sala de la función del booking
        4. Verificar que no exista un ticket duplicado para el mismo asiento y función
        """
        seat = data.get('seat')
        booking = data.get('booking')
        
        if not seat or not booking:
            raise serializers.ValidationError({
                "ticket": "Se requiere tanto el asiento como la reserva"
            })
            
        # Validar que el asiento esté disponible
        if not seat.seat_available:
            raise serializers.ValidationError({
                "seat": "El asiento no está disponible"
            })
            
        # Validar que el booking esté en estado válido
        if booking.status not in ['pending', 'confirmed']:
            raise serializers.ValidationError({
                "booking": "La reserva no está en un estado válido para crear tickets"
            })
            
        # Validar que el asiento pertenezca a la sala de la función
        if seat.hall != booking.function.hall:
            raise serializers.ValidationError({
                "seat": "El asiento no pertenece a la sala de la función"
            })
            
        # Verificar duplicados (excluyendo tickets cancelados)
        if Ticket.objects.filter(
            seat=seat,
            booking__function=booking.function,
            is_scanned=False
        ).exists():
            raise serializers.ValidationError({
                "ticket": "Ya existe un ticket activo para este asiento en esta función"
            })
            
        return data
    
    def create(self, validated_data):
        """
        Crea un nuevo ticket con los datos validados.
        """
        # Crear el ticket con los datos validados
        ticket = Ticket.objects.create(**validated_data)
        return ticket

    def update(self, instance, validated_data):
        """
        Actualiza un ticket existente con los datos validados.
        La lógica de negocio (liberación de asientos, notificaciones, etc.) se maneja en las views.
        """
        # Actualizar los campos del ticket
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Guardar los cambios
        instance.save()
        return instance


class ComboSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    combo_name = serializers.CharField(max_length=100)
    combo_description = serializers.CharField()
    combo_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    combo_picture = serializers.ImageField()

    def validate(self, data):
        """
        Validaciones a nivel de objeto:
        1. Validar que el nombre del combo no esté en uso
        2. Validar que el precio sea mayor que 0
        """
        if Combo.objects.filter(combo_name=data['combo_name']).exists():
            raise serializers.ValidationError({
                "combo_name": "Ya existe un combo con este nombre"
            })
        
        if data['combo_price'] <= 0:
            raise serializers.ValidationError({
                "combo_price": "El precio del combo debe ser mayor que 0"
            })
        
        return data
    
    def create(self, validated_data):
        """
        Crea un nuevo combo con los datos validados.
        """
        combo = Combo.objects.create(**validated_data)
        return combo

    def update(self, instance, validated_data):
        
        """
        Actualiza un combo existente con los datos validados.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class ComboTicketSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    booking = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all())
    combo = serializers.PrimaryKeyRelatedField(queryset=Combo.objects.all())
    quantity = serializers.IntegerField()
    total_combo_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    combo_ticket_code = serializers.CharField(read_only=True)
    issued_at = serializers.DateTimeField(read_only=True)
    is_scanned = serializers.BooleanField(read_only=True)
    
    def validate(self, data):
        """
        Validaciones a nivel de objeto:
        1. Verificar que el booking exista
        2. Verificar que el combo exista
        3. Validar que la cantidad sea positiva
        
        """
        booking = data.get('booking')
        combo = data.get('combo')
        quantity = data.get('quantity')

        if not booking or not combo:
            raise serializers.ValidationError({
                "combo_ticket": "Se requiere tanto el booking como el combo"
            })
        
        if quantity <= 0:
            raise serializers.ValidationError({
                "quantity": "La cantidad debe ser mayor que 0"
            })
        
        return data

    def create(self, validated_data):
        """
        Crea un nuevo combo ticket con los datos validados.
        """
        combo_ticket = ComboTicket.objects.create(**validated_data)
        return combo_ticket

    def update(self, instance, validated_data):
        """
        Actualiza un combo ticket existente con los datos validados.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance


