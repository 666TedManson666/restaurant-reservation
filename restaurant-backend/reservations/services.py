import logging
from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone

from .models import Reservation, RestaurantSchedule, Table

logger = logging.getLogger('reservations')


class AvailabilityError(Exception):
    """Raised when no tables are available."""
    pass


class ValidationError(Exception):
    """Raised when business rule is violated."""
    pass


def _get_reservation_end_time(reservation_time, duration_minutes):
    """Calculate the end time of a reservation."""
    dt = datetime.combine(datetime.today(), reservation_time)
    end_dt = dt + timedelta(minutes=duration_minutes)
    return end_dt.time()


def validate_reservation_time(date, time):
    """
    Ensure the requested date/time:
    - Is not in the past
    - Falls within restaurant schedule
    - Corresponds to a valid slot
    """
    schedule = RestaurantSchedule.get_schedule()
    now = timezone.localtime(timezone.now())
    requested_dt = datetime.combine(date, time)

    # Attach local timezone for comparison
    local_now = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)

    if requested_dt <= local_now:
        raise ValidationError("No se pueden realizar reservas en el pasado.")

    if time < schedule.opening_time or time >= schedule.closing_time:
        raise ValidationError(
            f"El horario del restaurante es de {schedule.opening_time.strftime('%H:%M')} "
            f"a {schedule.closing_time.strftime('%H:%M')}."
        )

    available_slots = schedule.get_available_slots()
    if time not in available_slots:
        raise ValidationError(
            f"La hora seleccionada no corresponde a un turno válido. "
            f"Turnos disponibles: {', '.join(s.strftime('%H:%M') for s in available_slots)}"
        )


def get_available_tables(date, time, guests):
    """
    Find all active tables with sufficient capacity that have no overlapping reservations.
    Returns queryset of available Table objects.
    """
    schedule = RestaurantSchedule.get_schedule()
    duration = schedule.reservation_duration_minutes

    reservation_start = datetime.combine(date, time)
    reservation_end = reservation_start + timedelta(minutes=duration)
    end_time = reservation_end.time()

    # Tables with enough capacity
    suitable_tables = Table.objects.filter(
        is_active=True,
        capacity__gte=guests
    )

    if not suitable_tables.exists():
        raise AvailabilityError("No hay mesas con capacidad suficiente para el número de personas solicitado.")

    # Find tables that have overlapping reservations
    occupied_table_ids = Reservation.objects.filter(
        date=date,
        status='confirmed',
        table__in=suitable_tables,
    ).filter(
        # Overlap condition: existing_start < new_end AND existing_end > new_start
        time__lt=end_time,
    ).filter(
        # We need to also check that existing reservation doesn't end before our start
        # Since we can't do time arithmetic in ORM easily, we filter conservatively
        # A reservation at 'r_time' ends at r_time + duration minutes
        # We filter:  r_time + duration > requested_time  =>  r_time > requested_time - duration
        time__gte=_subtract_minutes_from_time(time, duration)
    ).values_list('table_id', flat=True)

    available = suitable_tables.exclude(id__in=list(occupied_table_ids))

    if not available.exists():
        raise AvailabilityError("No hay disponibilidad para la fecha y hora seleccionadas.")

    return available


def _subtract_minutes_from_time(t, minutes):
    """Subtract minutes from a time object, returns time."""
    dt = datetime.combine(datetime.today(), t) - timedelta(minutes=minutes)
    return dt.time()


@transaction.atomic
def create_reservation(validated_data):
    """
    Atomically create a reservation:
    1. Validate date/time rules
    2. Lock available tables with select_for_update() to prevent concurrent booking
    3. Assign first available table
    4. Create reservation
    """
    date = validated_data['date']
    time = validated_data['time']
    guests = validated_data['guests']

    validate_reservation_time(date, time)

    schedule = RestaurantSchedule.get_schedule()
    duration = schedule.reservation_duration_minutes
    end_time = _get_reservation_end_time(time, duration)

    # Lock candidate tables to prevent concurrent booking
    suitable_tables = Table.objects.select_for_update().filter(
        is_active=True,
        capacity__gte=guests
    )

    if not suitable_tables.exists():
        raise AvailabilityError("No hay mesas con capacidad suficiente para el número de personas solicitado.")

    # Find occupied tables during this slot (with row-level lock)
    occupied_table_ids = Reservation.objects.select_for_update().filter(
        date=date,
        status='confirmed',
        table__in=suitable_tables,
        time__lt=end_time,
        time__gte=_subtract_minutes_from_time(time, duration)
    ).values_list('table_id', flat=True)

    available_table = suitable_tables.exclude(id__in=occupied_table_ids).first()

    if available_table is None:
        raise AvailabilityError("No hay disponibilidad para la fecha y hora seleccionadas.")

    reservation = Reservation.objects.create(
        table=available_table,
        **validated_data
    )

    logger.info(
        "Reservation created: %s | Date: %s %s | Table: %s | Guests: %s",
        reservation.id, date, time, available_table.number, guests
    )

    return reservation


@transaction.atomic
def cancel_reservation(reservation, cancelled_by_admin=False):
    """Cancel a reservation and free the table."""
    if reservation.status == 'cancelled':
        raise ValidationError("Esta reserva ya fue cancelada.")

    reservation.status = 'cancelled'
    reservation.save(update_fields=['status'])

    logger.info(
        "Reservation %s cancelled. Admin: %s", reservation.id, cancelled_by_admin
    )
    return reservation


def get_daily_occupancy(date):
    """
    Returns occupancy percentage for the given date.
    Occupancy = confirmed reservations / (total active tables * total slots)
    """
    schedule = RestaurantSchedule.get_schedule()
    total_tables = Table.objects.filter(is_active=True).count()
    total_slots = len(schedule.get_available_slots())
    total_capacity = total_tables * total_slots

    if total_capacity == 0:
        return 0

    confirmed = Reservation.objects.filter(date=date, status='confirmed').count()
    return round((confirmed / total_capacity) * 100, 1)
