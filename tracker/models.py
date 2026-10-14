from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'), ('manager', 'Manager'),
        ('user', 'User'), ('driver', 'Driver'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin'


class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'), ('idle', 'Idle'),
        ('maintenance', 'Maintenance'), ('offline', 'Offline'),
    ]
    TYPE_CHOICES = [
        ('car', 'Car'), ('truck', 'Truck'), ('bus', 'Bus'),
        ('motorcycle', 'Motorcycle'), ('van', 'Van'), ('ambulance', 'Ambulance'),
    ]
    FUEL_CHOICES = [
        ('petrol', 'Petrol'), ('diesel', 'Diesel'),
        ('electric', 'Electric'), ('cng', 'CNG'), ('hybrid', 'Hybrid'),
    ]

    name = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='car')
    make = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    year = models.IntegerField(default=2022)
    color = models.CharField(max_length=50, blank=True)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='petrol')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='idle')
    assigned_driver = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_vehicles'
    )
    latitude = models.FloatField(default=12.9716)
    longitude = models.FloatField(default=77.5946)
    speed = models.FloatField(default=0)
    fuel_level = models.FloatField(default=100)
    mileage = models.FloatField(default=0)
    insurance_expiry = models.DateField(null=True, blank=True)
    registration_expiry = models.DateField(null=True, blank=True)
    last_service_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle_number} – {self.name}"

    @property
    def status_color(self):
        return {
            'active': 'success', 'idle': 'warning',
            'maintenance': 'danger', 'offline': 'secondary',
        }.get(self.status, 'secondary')


class Driver(models.Model):
    LICENSE_CHOICES = [
        ('LMV', 'Light Motor Vehicle'),
        ('HMV', 'Heavy Motor Vehicle'),
        ('TRANS', 'Transport Vehicle'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=50, unique=True)
    license_type = models.CharField(max_length=20, choices=LICENSE_CHOICES, default='LMV')
    license_expiry = models.DateField()
    experience_years = models.IntegerField(default=0)
    rating = models.FloatField(default=5.0)
    total_trips = models.IntegerField(default=0)
    total_distance = models.FloatField(default=0)
    is_available = models.BooleanField(default=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    joining_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.get_full_name()} – {self.license_number}"


class Trip(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'), ('ongoing', 'Ongoing'),
        ('completed', 'Completed'), ('cancelled', 'Cancelled'),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='driven_trips'
    )
    start_location = models.CharField(max_length=200)
    end_location = models.CharField(max_length=200)
    scheduled_start = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    distance_km = models.FloatField(default=0)
    fuel_consumed = models.FloatField(default=0)
    purpose = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_trips'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trip #{self.id} | {self.vehicle.vehicle_number}"

    @property
    def status_color(self):
        return {
            'scheduled': 'warning', 'ongoing': 'primary',
            'completed': 'success', 'cancelled': 'secondary',
        }.get(self.status, 'secondary')


class Geofence(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    center_latitude = models.FloatField(default=12.9716)
    center_longitude = models.FloatField(default=77.5946)
    radius = models.FloatField(default=1000, help_text='Radius in metres')
    vehicles = models.ManyToManyField(Vehicle, blank=True, related_name='geofences')
    alert_on_entry = models.BooleanField(default=True)
    alert_on_exit = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Alert(models.Model):
    ALERT_TYPES = [
        ('speed', 'Speed Violation'), ('geofence', 'Geofence Breach'),
        ('fuel', 'Fuel Low'), ('maintenance', 'Maintenance Due'),
        ('accident', 'Accident'), ('idle', 'Long Idle'),
        ('tamper', 'Tamper Alert'), ('sos', 'SOS Emergency'),
    ]
    SEVERITY = [
        ('low', 'Low'), ('medium', 'Medium'),
        ('high', 'High'), ('critical', 'Critical'),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY, default='medium')
    message = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resolved_alerts'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_alert_type_display()} – {self.vehicle.vehicle_number}"

    @property
    def severity_color(self):
        return {
            'low': 'info', 'medium': 'warning',
            'high': 'danger', 'critical': 'danger',
        }.get(self.severity, 'secondary')


class MaintenanceRecord(models.Model):
    SERVICE_TYPES = [
        ('oil_change', 'Oil Change'), ('tire_rotation', 'Tyre Rotation'),
        ('brake_service', 'Brake Service'), ('engine_service', 'Engine Service'),
        ('battery', 'Battery Replacement'), ('ac_service', 'AC Service'),
        ('general', 'General Service'), ('repair', 'Repair'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'), ('in_progress', 'In Progress'),
        ('completed', 'Completed'), ('cancelled', 'Cancelled'),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_records')
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES)
    service_center = models.CharField(max_length=200, blank=True)
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mileage_at_service = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    technician_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    next_service_due = models.DateField(null=True, blank=True)
    next_service_mileage = models.FloatField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle.vehicle_number} – {self.get_service_type_display()} – {self.scheduled_date}"

    @property
    def status_color(self):
        return {
            'scheduled': 'warning', 'in_progress': 'primary',
            'completed': 'success', 'cancelled': 'secondary',
        }.get(self.status, 'secondary')


class FuelRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='fuel_records')
    driver = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='fuel_records'
    )
    date = models.DateTimeField(default=timezone.now)
    fuel_quantity = models.FloatField(help_text='Litres')
    fuel_cost = models.DecimalField(max_digits=10, decimal_places=2)
    mileage_at_fill = models.FloatField(default=0)
    station_name = models.CharField(max_length=200, blank=True)
    receipt_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle.vehicle_number} – {self.fuel_quantity}L – {self.date.date()}"


class Report(models.Model):
    REPORT_TYPES = [
        ('vehicle_summary', 'Vehicle Summary'),
        ('trip_report', 'Trip Report'),
        ('fuel_report', 'Fuel Report'),
        ('maintenance_report', 'Maintenance Report'),
        ('driver_report', 'Driver Report'),
        ('alert_report', 'Alert Report'),
    ]
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} – {self.created_at.date()}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} – {self.title}"

    class Meta:
        ordering = ['-created_at']


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} – {self.subject}"


# ── Auto-create UserProfile when a User is created ──────────────────────────
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
