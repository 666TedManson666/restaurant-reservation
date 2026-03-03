import threading
from datetime import date, time, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Reservation, RestaurantSchedule, Table
from .services import (
    AvailabilityError,
    ValidationError,
    create_reservation,
    get_available_tables,
    validate_reservation_time,
)


def get_future_date(days=1):
    return timezone.localdate() + timedelta(days=days)


def setup_schedule(opening='12:00', closing='23:00', interval=60, duration=90):
    schedule = RestaurantSchedule.get_schedule()
    from datetime import time as t
    schedule.opening_time = t(*map(int, opening.split(':')))
    schedule.closing_time = t(*map(int, closing.split(':')))
    schedule.slot_interval_minutes = interval
    schedule.reservation_duration_minutes = duration
    schedule.save()
    return schedule


class TableModelTests(TestCase):
    def setUp(self):
        self.table = Table.objects.create(number='T1', capacity=4, is_active=True)

    def test_table_str(self):
        self.assertIn('T1', str(self.table))

    def test_has_future_reservations_false_when_empty(self):
        self.assertFalse(self.table.has_future_reservations())

    def test_has_future_reservations_true(self):
        setup_schedule()
        Reservation.objects.create(
            name='Test', email='test@test.com', phone='123',
            date=get_future_date(), time=time(12, 0), guests=2,
            table=self.table, status='confirmed'
        )
        self.assertTrue(self.table.has_future_reservations())


class AvailabilityServiceTests(TestCase):
    def setUp(self):
        setup_schedule()
        Table.objects.create(number='T1', capacity=4, is_active=True)
        Table.objects.create(number='T2', capacity=4, is_active=True)

    def test_tables_available_when_no_reservations(self):
        available = get_available_tables(get_future_date(), time(12, 0), 2)
        self.assertEqual(available.count(), 2)

    def test_no_tables_when_all_occupied(self):
        date = get_future_date()
        reservation_time = time(12, 0)
        for table in Table.objects.all():
            Reservation.objects.create(
                name='Test', email='t@t.com', phone='123',
                date=date, time=reservation_time, guests=2,
                table=table, status='confirmed'
            )
        with self.assertRaises(AvailabilityError):
            get_available_tables(date, reservation_time, 2)

    def test_insufficient_capacity_raises_error(self):
        """Case 2: all tables are 4-person, client requests 8."""
        with self.assertRaises(AvailabilityError):
            get_available_tables(get_future_date(), time(12, 0), 8)

    def test_inactive_table_not_returned(self):
        Table.objects.create(number='T3', capacity=4, is_active=False)
        available = get_available_tables(get_future_date(), time(12, 0), 2)
        self.assertFalse(available.filter(number='T3').exists())


class ValidationServiceTests(TestCase):
    def setUp(self):
        setup_schedule()

    def test_past_date_rejected(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            validate_reservation_time(yesterday, time(12, 0))

    def test_outside_schedule_rejected(self):
        with self.assertRaises(ValidationError):
            validate_reservation_time(get_future_date(), time(6, 0))

    def test_invalid_slot_rejected(self):
        """Slot not aligned to interval should be rejected."""
        with self.assertRaises(ValidationError):
            validate_reservation_time(get_future_date(), time(12, 30))

    def test_valid_slot_accepted(self):
        # Should not raise
        validate_reservation_time(get_future_date(), time(12, 0))


class CreateReservationTests(TestCase):
    def setUp(self):
        setup_schedule()
        self.table = Table.objects.create(number='T1', capacity=4, is_active=True)

    def _data(self, **kwargs):
        defaults = {
            'name': 'Juan Pérez',
            'email': 'juan@test.com',
            'phone': '3001234567',
            'date': get_future_date(),
            'time': time(12, 0),
            'guests': 2,
            'notes': '',
        }
        defaults.update(kwargs)
        return defaults

    def test_valid_reservation_created(self):
        reservation = create_reservation(self._data())
        self.assertEqual(reservation.status, 'confirmed')
        self.assertEqual(reservation.table, self.table)

    def test_no_tables_available_raises_error(self):
        """Case 1: all tables full at a given time."""
        data = self._data()
        # Fill the only table
        Reservation.objects.create(
            name='Other', email='o@t.com', phone='000',
            date=data['date'], time=data['time'], guests=2,
            table=self.table, status='confirmed'
        )
        with self.assertRaises(AvailabilityError):
            create_reservation(data)

    def test_cancel_code_is_generated(self):
        reservation = create_reservation(self._data())
        self.assertIsNotNone(reservation.cancel_code)

    def test_past_reservation_rejected(self):
        from datetime import date as d
        yesterday = timezone.localdate() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            create_reservation(self._data(date=yesterday))


class ConcurrencyTest(TestCase):
    """
    Case 3: Sequential simulation of concurrent bookings on the last available table.
    select_for_update() works correctly with PostgreSQL in production;
    here we simulate the race condition sequentially.
    """

    def setUp(self):
        setup_schedule()
        Table.objects.create(number='T1', capacity=4, is_active=True)

    def _reservation_data(self, index):
        return {
            'name': f'User{index}',
            'email': f'user{index}@test.com',
            'phone': '000',
            'date': get_future_date(),
            'time': time(12, 0),
            'guests': 2,
            'notes': '',
        }

    def test_only_one_reservation_allowed_when_table_full(self):
        """First booking succeeds; second booking on same slot must fail."""
        # First user books successfully
        r1 = create_reservation(self._reservation_data(0))
        self.assertEqual(r1.status, 'confirmed')

        # Second user attempts same slot — must fail
        with self.assertRaises(AvailabilityError):
            create_reservation(self._reservation_data(1))

        self.assertEqual(Reservation.objects.filter(status='confirmed').count(), 1)


class ReservationAPITests(APITestCase):
    def setUp(self):
        setup_schedule()
        self.table = Table.objects.create(number='T1', capacity=4, is_active=True)
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'adminpass')

    def get_admin_token(self):
        refresh = RefreshToken.for_user(self.admin_user)
        return str(refresh.access_token)

    def test_get_availability(self):
        response = self.client.get(f'/api/availability/?date={get_future_date()}&guests=2')
        self.assertEqual(response.status_code, 200)
        self.assertIn('available_slots', response.data)

    def test_create_reservation_api(self):
        data = {
            'name': 'Ana',
            'email': 'ana@test.com',
            'phone': '3009999999',
            'date': str(get_future_date()),
            'time': '12:00',
            'guests': 2,
        }
        response = self.client.post('/api/reservations/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('cancel_code', response.data)

    def test_cancel_reservation_via_code(self):
        reservation = create_reservation({
            'name': 'Test', 'email': 't@t.com', 'phone': '000',
            'date': get_future_date(), 'time': time(12, 0), 'guests': 2, 'notes': ''
        })
        response = self.client.post('/api/reservations/cancel/', {'cancel_code': str(reservation.cancel_code)}, format='json')
        self.assertEqual(response.status_code, 200)
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, 'cancelled')

    def test_admin_table_crud(self):
        token = self.get_admin_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        # Create
        resp = self.client.post('/api/admin/tables/', {'number': 'T99', 'capacity': 6, 'is_active': True}, format='json')
        self.assertEqual(resp.status_code, 201)
        # List
        resp = self.client.get('/api/admin/tables/')
        self.assertEqual(resp.status_code, 200)

    def test_admin_metrics(self):
        token = self.get_admin_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resp = self.client.get(f'/api/admin/metrics/?date={get_future_date()}')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('occupancy_percentage', resp.data)
