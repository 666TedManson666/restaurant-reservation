import logging

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Reservation, RestaurantSchedule, Table
from .serializers import (
    AvailabilitySerializer,
    CancelReservationSerializer,
    CreateReservationSerializer,
    ReservationSerializer,
    RestaurantScheduleSerializer,
    TableSerializer,
)
from .services import AvailabilityError
from .services import ValidationError as ServiceValidationError

logger = logging.getLogger('reservations')


# ─── Public Views ──────────────────────────────────────────────────────────────

class AvailabilityView(APIView):
    """GET /api/availability/?date=YYYY-MM-DD&guests=N"""
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = AvailabilitySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        date = serializer.validated_data['date']
        guests = serializer.validated_data.get('guests', 1)
        schedule = RestaurantSchedule.get_schedule()

        try:
            # Validate day-level availability
            from datetime import datetime, timedelta
            available_slots = []
            for slot_time in schedule.get_available_slots():
                slot_dt = datetime.combine(date, slot_time)
                local_now = datetime.now()
                if slot_dt <= local_now:
                    continue
                try:
                    available_tables = services.get_available_tables(date, slot_time, guests)
                    if available_tables.exists():
                        available_slots.append({
                            'time': slot_time.strftime('%H:%M'),
                            'available_tables': available_tables.count(),
                        })
                except AvailabilityError:
                    pass

            return Response({
                'date': date,
                'guests': guests,
                'schedule': {
                    'opening_time': schedule.opening_time.strftime('%H:%M'),
                    'closing_time': schedule.closing_time.strftime('%H:%M'),
                    'slot_interval_minutes': schedule.slot_interval_minutes,
                    'reservation_duration_minutes': schedule.reservation_duration_minutes,
                },
                'available_slots': available_slots,
            })

        except ServiceValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReservationCreateView(APIView):
    """POST /api/reservations/"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CreateReservationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            reservation = services.create_reservation(serializer.validated_data)
            out = ReservationSerializer(reservation)
            return Response(out.data, status=status.HTTP_201_CREATED)

        except ServiceValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except AvailabilityError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReservationCancelPublicView(APIView):
    """POST /api/reservations/cancel/  — cancel via cancel_code"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CancelReservationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cancel_code = serializer.validated_data['cancel_code']
        reservation = get_object_or_404(Reservation, cancel_code=cancel_code)

        try:
            services.cancel_reservation(reservation)
            return Response({'detail': 'Reserva cancelada exitosamente.'})
        except ServiceValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ─── Admin Views ───────────────────────────────────────────────────────────────

class AdminTableViewSet(viewsets.ModelViewSet):
    """CRUD for tables – Admin only."""
    queryset = Table.objects.all().order_by('number')
    serializer_class = TableSerializer
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        table = self.get_object()
        if table.has_future_reservations():
            return Response(
                {'detail': 'No se puede eliminar una mesa con reservas futuras confirmadas.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class AdminScheduleView(APIView):
    """GET/PUT restaurant schedule – Admin only."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        schedule = RestaurantSchedule.get_schedule()
        return Response(RestaurantScheduleSerializer(schedule).data)

    def put(self, request):
        schedule = RestaurantSchedule.get_schedule()
        serializer = RestaurantScheduleSerializer(schedule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        schedule = RestaurantSchedule.get_schedule()
        serializer = RestaurantScheduleSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminReservationViewSet(viewsets.ReadOnlyModelViewSet):
    """List and filter reservations – Admin only."""
    serializer_class = ReservationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = Reservation.objects.select_related('table').all()
        date = self.request.query_params.get('date')
        status_filter = self.request.query_params.get('status')

        if date:
            qs = qs.filter(date=date)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """POST /api/admin/reservations/{id}/cancel/"""
        reservation = self.get_object()
        try:
            services.cancel_reservation(reservation, cancelled_by_admin=True)
            return Response({'detail': 'Reserva cancelada.'})
        except ServiceValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminMetricsView(APIView):
    """GET /api/admin/metrics/?date=YYYY-MM-DD"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        from django.db.models import Count
        from django.utils import timezone

        date_str = request.query_params.get('date')
        if date_str:
            from datetime import date as date_type
            try:
                from datetime import datetime
                query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'detail': 'Formato de fecha inválido. Use YYYY-MM-DD.'}, status=400)
        else:
            query_date = timezone.localdate()

        occupancy = services.get_daily_occupancy(query_date)
        confirmed_count = Reservation.objects.filter(date=query_date, status='confirmed').count()
        cancelled_count = Reservation.objects.filter(date=query_date, status='cancelled').count()
        total_active_tables = Table.objects.filter(is_active=True).count()

        return Response({
            'date': query_date,
            'confirmed_reservations': confirmed_count,
            'cancelled_reservations': cancelled_count,
            'total_active_tables': total_active_tables,
            'occupancy_percentage': occupancy,
        })
