from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'admin/tables', views.AdminTableViewSet, basename='admin-tables')
router.register(r'admin/reservations', views.AdminReservationViewSet, basename='admin-reservations')

urlpatterns = [
    # Public endpoints
    path('availability/', views.AvailabilityView.as_view(), name='availability'),
    path('reservations/', views.ReservationCreateView.as_view(), name='reservation-create'),
    path('reservations/cancel/', views.ReservationCancelPublicView.as_view(), name='reservation-cancel-public'),

    # Admin endpoints
    path('admin/schedule/', views.AdminScheduleView.as_view(), name='admin-schedule'),
    path('admin/metrics/', views.AdminMetricsView.as_view(), name='admin-metrics'),

    # Router-based viewsets
    path('', include(router.urls)),
]
