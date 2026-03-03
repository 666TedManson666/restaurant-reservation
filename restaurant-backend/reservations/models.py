import uuid
from django.db import models


STATUS_CHOICES = [
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),
]


class Table(models.Model):
    number = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Mesa {self.number} ({self.capacity} pax)"

    def has_future_reservations(self):
        from django.utils import timezone
        today = timezone.localdate()
        return self.reservation_set.filter(
            date__gte=today,
            status='confirmed'
        ).exists()


class RestaurantSchedule(models.Model):
    """Singleton model — only one row should exist."""
    opening_time = models.TimeField(default='12:00')
    closing_time = models.TimeField(default='22:00')
    slot_interval_minutes = models.IntegerField(default=60, help_text='Minutes between bookable slots')
    reservation_duration_minutes = models.IntegerField(default=90, help_text='Duration of each reservation in minutes')

    class Meta:
        verbose_name = 'Restaurant Schedule'
        verbose_name_plural = 'Restaurant Schedule'

    def __str__(self):
        return f"Schedule {self.opening_time} - {self.closing_time}"

    @classmethod
    def get_schedule(cls):
        schedule, _ = cls.objects.get_or_create(pk=1)
        return schedule

    def get_available_slots(self):
        """Return list of time slots based on opening_time, closing_time, and interval."""
        from datetime import datetime, timedelta
        slots = []
        current = datetime.combine(datetime.today(), self.opening_time)
        end = datetime.combine(datetime.today(), self.closing_time)
        duration = timedelta(minutes=self.reservation_duration_minutes)
        interval = timedelta(minutes=self.slot_interval_minutes)

        while current + duration <= end:
            slots.append(current.time())
            current += interval
        return slots


class Reservation(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    guests = models.IntegerField()
    table = models.ForeignKey(Table, on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    cancel_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['cancel_code']),
        ]

    def __str__(self):
        return f"{self.name} - Mesa {self.table} el {self.date} a las {self.time}"
