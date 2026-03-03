from django.contrib import admin
from .models import Reservation, RestaurantSchedule, Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'capacity', 'is_active']
    list_filter = ['is_active']
    search_fields = ['number']


@admin.register(RestaurantSchedule)
class RestaurantScheduleAdmin(admin.ModelAdmin):
    list_display = ['opening_time', 'closing_time', 'slot_interval_minutes', 'reservation_duration_minutes']

    def has_add_permission(self, request):
        # Only allow one schedule object
        return not RestaurantSchedule.objects.exists()


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'date', 'time', 'guests', 'table', 'status', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['name', 'email', 'phone']
    date_hierarchy = 'date'
    readonly_fields = ['cancel_code', 'created_at']
