import random
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from tracker.models import (
    UserProfile, Vehicle, Driver, Trip, Geofence,
    Alert, MaintenanceRecord, FuelRecord, Notification, Contact,
)


class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('\n  Seeding database…\n'))

        # ── admin ──────────────────────────────────────────────────────
        admin, created = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@avtpro.in', 'first_name': 'Admin', 'last_name': 'User',
            'is_staff': True, 'is_superuser': True,
        })
        if created:
            admin.set_password('admin123')
            admin.save()
            UserProfile.objects.create(user=admin, role='admin', phone='+91 98765 43210', department='Management')
            self.stdout.write(self.style.SUCCESS('  ✔  admin / admin123'))
        else:
            self.stdout.write('  →  admin already exists')

        # ── regular users ──────────────────────────────────────────────
        users_data = [
            ('user1',   'Rahul',  'Sharma', 'rahul@example.com',   'user123',   'user',    '+91 98100 11111', 'Operations'),
            ('user2',   'Priya',  'Patel',  'priya@example.com',   'user123',   'manager', '+91 98100 22222', 'Fleet'),
            ('driver1', 'Suresh', 'Kumar',  'suresh@example.com',  'driver123', 'driver',  '+91 98100 33333', 'Drivers'),
            ('driver2', 'Ramesh', 'Singh',  'ramesh@example.com',  'driver123', 'driver',  '+91 98100 44444', 'Drivers'),
            ('driver3', 'Vikram', 'Rao',    'vikram@example.com',  'driver123', 'driver',  '+91 98100 55555', 'Drivers'),
        ]
        user_map = {'admin': admin}
        for uname, fname, lname, email, pwd, role, phone, dept in users_data:
            u, created = User.objects.get_or_create(username=uname, defaults={
                'email': email, 'first_name': fname, 'last_name': lname,
            })
            if created:
                u.set_password(pwd)
                u.save()
                UserProfile.objects.create(user=u, role=role, phone=phone, department=dept)
                self.stdout.write(self.style.SUCCESS(f'  ✔  {uname} / {pwd}'))
            user_map[uname] = u

        # ── driver profiles ────────────────────────────────────────────
        for uname, lic, ltype, expiry, exp, rating in [
            ('driver1', 'KA0120230001', 'LMV',   date(2026, 6,  30), 5, 4.8),
            ('driver2', 'KA0120230002', 'HMV',   date(2025, 12, 31), 8, 4.6),
            ('driver3', 'KA0120230003', 'TRANS', date(2027, 3,  15), 3, 4.9),
        ]:
            u = user_map.get(uname)
            if u and not Driver.objects.filter(user=u).exists():
                Driver.objects.create(
                    user=u, license_number=lic, license_type=ltype,
                    license_expiry=expiry, experience_years=exp, rating=rating,
                    total_trips=random.randint(50, 300),
                    total_distance=round(random.uniform(5000, 50000), 1),
                    joining_date=date(2021, random.randint(1, 12), 15),
                    emergency_contact='+91 99999 00000',
                )

        # ── vehicles ───────────────────────────────────────────────────
        vdata = [
            ('KA01AB1234', 'Fleet Car 1',      'car',        'Toyota',    'Innova Crysta', 2022, 'White',  'diesel',  'active',      'driver1', 12.9716, 77.5946, 78,  18250),
            ('KA01CD5678', 'Fleet Car 2',       'car',        'Honda',     'City',          2021, 'Silver', 'petrol',  'active',      'driver2', 12.9352, 77.6245, 62,  35400),
            ('KA01EF9012', 'Delivery Truck 1',  'truck',      'Tata',      'LPT 1109',      2020, 'Blue',   'diesel',  'active',      'driver3', 12.9800, 77.6200, 45,  82100),
            ('KA01GH3456', 'Staff Van',         'van',        'Force',     'Traveller',     2023, 'White',  'diesel',  'idle',        None,      12.9600, 77.5800, 89,   5200),
            ('KA01IJ7890', 'Executive Car',     'car',        'Mercedes',  'E-Class',       2022, 'Black',  'petrol',  'idle',        None,      12.9400, 77.6100, 55,  12000),
            ('KA01KL2345', 'Heavy Truck 1',     'truck',      'Ashok L.',  '1916',          2019, 'Red',    'diesel',  'maintenance', None,      12.9500, 77.5700, 30, 145000),
            ('KA01MN6789', 'Courier Bike 1',    'motorcycle', 'Honda',     'Activa',        2023, 'Blue',   'petrol',  'active',      None,      12.9650, 77.6050, 95,   8500),
            ('KA01OP1234', 'School Bus 1',      'bus',        'TATA',      'Starbus Ultra', 2021, 'Yellow', 'diesel',  'idle',        None,      12.9700, 77.5850, 71,  65000),
            ('KA01QR5678', 'Ambulance 1',       'ambulance',  'Force',     'Trax Cruiser',  2022, 'White',  'diesel',  'active',      None,      12.9550, 77.6150, 88,  22500),
            ('KA01ST9012', 'CNG City Taxi',     'car',        'Maruti',    'Dzire',         2023, 'Grey',   'cng',     'idle',        None,      12.9480, 77.5980, 100, 31200),
        ]
        vehicles = []
        for vnum, name, vtype, make, model, year, color, fuel, status, driver_key, lat, lng, fuel_lv, mileage in vdata:
            driver_user = user_map.get(driver_key) if driver_key else None
            v, created = Vehicle.objects.get_or_create(vehicle_number=vnum, defaults=dict(
                name=name, vehicle_type=vtype, make=make, model=model, year=year,
                color=color, fuel_type=fuel, status=status, assigned_driver=driver_user,
                latitude=lat, longitude=lng, fuel_level=fuel_lv, mileage=mileage,
                insurance_expiry=date(2025, random.randint(1, 12), 28),
                registration_expiry=date(2026, random.randint(1, 12), 28),
                last_service_date=date.today() - timedelta(days=random.randint(30, 180)),
            ))
            vehicles.append(v)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✔  Vehicle {vnum}'))

        # ── trips ──────────────────────────────────────────────────────
        if Trip.objects.count() < 5:
            trips_raw = [
                ('Bengaluru Airport', 'Whitefield IT Park',  'completed', -4,  22.5, 2.1),
                ('Koramangala',       'Electronic City',      'completed', -2,  18.3, 1.8),
                ('MG Road',           'Indiranagar',          'ongoing',    0,   8.5, 0.0),
                ('Jayanagar',         'HSR Layout',           'scheduled',  1,   0.0, 0.0),
                ('Hebbal',            'Mysore Road',          'completed', -6,  35.2, 3.4),
                ('BTM Layout',        'Sarjapur Road',        'completed', -1,  14.8, 1.5),
                ('Yeshwanthpur',      'Tumkur Road',          'ongoing',    0,  12.1, 0.0),
                ('Marathahalli',      'Outer Ring Road',      'scheduled',  3,   0.0, 0.0),
            ]
            drivers_list = [user_map['driver1'], user_map['driver2'], user_map['driver3']]
            for i, (s, e, status, doff, dist, fc) in enumerate(trips_raw):
                sch = timezone.now() + timedelta(days=doff)
                Trip.objects.create(
                    vehicle=vehicles[i % len(vehicles)],
                    driver=drivers_list[i % 3],
                    start_location=s, end_location=e,
                    scheduled_start=sch,
                    actual_start=sch if status in ('ongoing', 'completed') else None,
                    actual_end=sch + timedelta(hours=2) if status == 'completed' else None,
                    status=status, distance_km=dist, fuel_consumed=fc,
                    purpose='Official duty', created_by=admin,
                )
            self.stdout.write(self.style.SUCCESS(f'  ✔  {len(trips_raw)} trips'))

        # ── alerts ─────────────────────────────────────────────────────
        if Alert.objects.count() < 5:
            alerts_raw = [
                ('speed',       'high',     'Vehicle exceeded 80 km/h limit. Recorded: 97 km/h.'),
                ('fuel',        'medium',   'Fuel level below 20%. Refuelling required soon.'),
                ('geofence',    'high',     'Vehicle exited the designated geofence zone.'),
                ('idle',        'low',      'Vehicle idling for more than 45 minutes.'),
                ('maintenance', 'medium',   'Service overdue by 2,500 km. Schedule maintenance.'),
                ('sos',         'critical', 'SOS emergency triggered by driver!'),
                ('tamper',      'critical', 'GPS tamper detected on device.'),
                ('speed',       'medium',   'Speed exceeded in school zone (60 km/h limit).'),
            ]
            for i, (atype, sev, msg) in enumerate(alerts_raw):
                v = vehicles[i % len(vehicles)]
                Alert.objects.create(
                    vehicle=v, alert_type=atype, severity=sev, message=msg,
                    latitude=v.latitude, longitude=v.longitude,
                    is_read=random.choice([True, False]),
                    is_resolved=random.choice([True, False]),
                )
            self.stdout.write(self.style.SUCCESS(f'  ✔  {len(alerts_raw)} alerts'))

        # ── maintenance ────────────────────────────────────────────────
        if MaintenanceRecord.objects.count() < 3:
            maint_raw = [
                ('oil_change',    'completed',  -60, 800,  'Speedy Service Koramangala', 'John Tech'),
                ('tire_rotation', 'completed',  -30, 500,  'MRF Service Center BTM',     'Raj Kumar'),
                ('brake_service', 'scheduled',   15, 3500, 'Bosch Service Whitefield',   'Service Team'),
                ('engine_service','in_progress',  0, 8000, 'TATA Authorized Hebbal',     'Expert Mech'),
                ('ac_service',    'completed',  -90, 1200, 'Cool Zone Indiranagar',      'AC Expert'),
                ('battery',       'scheduled',   30, 4500, 'Exide Service MG Road',      'Battery Tech'),
            ]
            for i, (stype, status, doff, cost, center, tech) in enumerate(maint_raw):
                v = vehicles[i % len(vehicles)]
                sd = date.today() + timedelta(days=doff)
                MaintenanceRecord.objects.create(
                    vehicle=v, service_type=stype, status=status,
                    scheduled_date=sd,
                    completed_date=sd if status == 'completed' else None,
                    cost=cost, service_center=center, technician_name=tech,
                    mileage_at_service=v.mileage - 2000,
                    next_service_due=sd + timedelta(days=90),
                    created_by=admin,
                )
            self.stdout.write(self.style.SUCCESS(f'  ✔  {len(maint_raw)} maintenance records'))

        # ── fuel records ───────────────────────────────────────────────
        if FuelRecord.objects.count() < 5:
            stations = ['HPCL Koramangala', 'BPCL MG Road', 'Indian Oil BTM', 'Shell Whitefield', 'HPCL Hebbal']
            drivers_list = [user_map['driver1'], user_map['driver2'], user_map['driver3']]
            recs = []
            for i in range(15):
                v = vehicles[i % len(vehicles)]
                qty  = round(random.uniform(20, 60), 2)
                cost = round(qty * random.uniform(92, 106), 2)
                recs.append(FuelRecord(
                    vehicle=v, driver=drivers_list[i % 3],
                    date=timezone.now() - timedelta(days=random.randint(1, 60)),
                    fuel_quantity=qty, fuel_cost=cost,
                    mileage_at_fill=v.mileage - random.randint(0, 5000),
                    station_name=random.choice(stations),
                    receipt_number=f'RCP{random.randint(100000,999999)}',
                ))
            FuelRecord.objects.bulk_create(recs)
            self.stdout.write(self.style.SUCCESS('  ✔  15 fuel records'))

        # ── geofences ──────────────────────────────────────────────────
        if Geofence.objects.count() < 2:
            zones = [
                ('Bengaluru City Zone',   12.9716, 77.5946, 10000),
                ('Airport Zone',          13.1986, 77.7066,  2000),
                ('Electronic City Zone',  12.8399, 77.6770,  3000),
                ('Night Restricted Zone', 12.9700, 77.5900,  5000),
            ]
            for name, lat, lng, r in zones:
                g = Geofence.objects.create(
                    name=name, center_latitude=lat, center_longitude=lng,
                    radius=r, is_active=True, alert_on_entry=True, alert_on_exit=True,
                    created_by=admin,
                )
                for v in vehicles[:3]:
                    g.vehicles.add(v)
            self.stdout.write(self.style.SUCCESS(f'  ✔  {len(zones)} geofences'))

        # ── notifications ──────────────────────────────────────────────
        if Notification.objects.count() < 3:
            notif_data = [
                ('Welcome to AutoVehicle Tracker!', 'Your account is set up. Start with the Live Tracking map.', 'info'),
                ('Speed Violation Alert',            'KA01AB1234 exceeded speed limit. Check Alerts.', 'warning'),
                ('Maintenance Due',                  'Fleet Car 2 service due in 3 days.', 'warning'),
                ('Trip Completed',                   'Trip #1 Bengaluru Airport → Whitefield completed.', 'success'),
                ('System Update',                    'Platform updated to v2.5. New geofence features available.', 'info'),
            ]
            for title, msg, ntype in notif_data:
                Notification.objects.create(user=admin, title=title, message=msg, notification_type=ntype)
            self.stdout.write(self.style.SUCCESS(f'  ✔  {len(notif_data)} notifications'))

        # ── contacts ───────────────────────────────────────────────────
        if Contact.objects.count() < 2:
            contacts_data = [
                ('Ajay Mehta',   'ajay@logistics.com', 'Fleet Pricing Query',         'I manage 35 trucks. Can you share pricing details?', False),
                ('Neha Gupta',   'neha@startup.in',    'Demo Request',                'We have 10 vehicles. Would love a demo.', False),
                ('Ravi Shankar', 'ravi@corp.com',       'ERP Integration',             'Does your platform integrate with SAP/Tally?', True),
                ('Pooja Singh',  'pooja@transport.co', 'Support – GPS Offline',       'One vehicle shows offline but is running. Help!', False),
            ]
            for name, email, subject, msg, replied in contacts_data:
                Contact.objects.create(name=name, email=email, subject=subject, message=msg, is_replied=replied)
            self.stdout.write(self.style.SUCCESS(f'  ✔  {len(contacts_data)} contacts'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('  ══════════════════════════════════════'))
        self.stdout.write(self.style.SUCCESS('   Database seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('  ══════════════════════════════════════'))
        self.stdout.write('')
        self.stdout.write('  Login credentials:')
        self.stdout.write('    Admin   →  admin   / admin123')
        self.stdout.write('    User    →  user1   / user123')
        self.stdout.write('    Manager →  user2   / user123')
        self.stdout.write('    Driver  →  driver1 / driver123')
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('  Open: http://127.0.0.1:8000'))
        self.stdout.write('')
