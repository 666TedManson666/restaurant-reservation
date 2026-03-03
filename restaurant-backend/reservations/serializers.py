from datetime import date as date_type

from django.utils import timezone
from rest_framework import serializers

from .models import Reservation, RestaurantSchedule, Table


class TableSerializer(serializers.ModelSerializer):
    has_future_reservations = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ['id', 'number', 'capacity', 'is_active', 'has_future_reservations']

    def get_has_future_reservations(self, obj):
        return obj.has_future_reservations()


class RestaurantScheduleSerializer(serializers.ModelSerializer):
    available_slots = serializers.SerializerMethodField()

    class Meta:
        model = RestaurantSchedule
        fields = [
            'id', 'opening_time', 'closing_time',
            'slot_interval_minutes', 'reservation_duration_minutes',
            'available_slots'
        ]

    def get_available_slots(self, obj):
        return [t.strftime('%H:%M') for t in obj.get_available_slots()]


class ReservationSerializer(serializers.ModelSerializer):
    table_number = serializers.CharField(source='table.number', read_only=True)
    table_capacity = serializers.IntegerField(source='table.capacity', read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'name', 'email', 'phone', 'date', 'time', 'guests',
            'table', 'table_number', 'table_capacity', 'status',
            'cancel_code', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'table', 'table_number', 'table_capacity', 'status', 'cancel_code', 'created_at']

    def validate_date(self, value):
        today = timezone.localdate()
        if value < today:
            raise serializers.ValidationError("No se pueden realizar reservas en el pasado.")
        return value

    def validate_guests(self, value):
        if value < 1:
            raise serializers.ValidationError("El número de personas debe ser al menos 1.")
        if value > 20:
            raise serializers.ValidationError("El número máximo de personas por reserva es 20.")
        return value

    def validate_email(self, value):
        return value.lower().strip()


class CreateReservationSerializer(serializers.Serializer):
    """Input serializer for creating reservations — validation happens in service layer."""
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    date = serializers.DateField()
    time = serializers.TimeField()
    guests = serializers.IntegerField(min_value=1, max_value=20)
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_date(self, value):
        today = timezone.localdate()
        if value < today:
            raise serializers.ValidationError("No se pueden realizar reservas en el pasado.")
        return value

    def validate_email(self, value):
        return value.lower().strip()


class AvailabilitySerializer(serializers.Serializer):
    date = serializers.DateField()
    guests = serializers.IntegerField(required=False, default=1, min_value=1)

    def validate_date(self, value):
        today = timezone.localdate()
        if value < today:
            raise serializers.ValidationError("No se puede consultar disponibilidad para fechas pasadas.")
        return value


class CancelReservationSerializer(serializers.Serializer):
    cancel_code = serializers.UUIDField()
