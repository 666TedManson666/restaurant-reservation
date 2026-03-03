from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from reservations.models import RestaurantSchedule, Table


class Command(BaseCommand):
    help = 'Seed initial data: admin user, restaurant schedule, sample tables'

    def handle(self, *args, **options):
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@mesareserva.com', 'Admin1234!')
            self.stdout.write(self.style.SUCCESS('✓ Superusuario creado: admin / Admin1234!'))
        else:
            self.stdout.write('  Admin already exists, skipping.')

        # Create schedule
        schedule = RestaurantSchedule.get_schedule()
        from datetime import time
        schedule.opening_time = time(12, 0)
        schedule.closing_time = time(23, 0)
        schedule.slot_interval_minutes = 60
        schedule.reservation_duration_minutes = 90
        schedule.save()
        self.stdout.write(self.style.SUCCESS('✓ Horario configurado: 12:00 - 23:00 (turnos cada 60min)'))

        # Create tables
        tables_data = [
            ('T1', 2), ('T2', 2), ('T3', 4), ('T4', 4), ('T5', 4),
            ('T6', 6), ('T7', 6), ('T8', 8),
        ]
        created = 0
        for number, capacity in tables_data:
            _, was_created = Table.objects.get_or_create(
                number=number,
                defaults={'capacity': capacity, 'is_active': True}
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'✓ {created} mesas creadas ({len(tables_data)} total)'))
        self.stdout.write(self.style.SUCCESS('\n🎉 Datos iniciales creados correctamente.'))
