from django.contrib import admin
from .models import (
    UserProfile, Vehicle, Driver, Trip, Geofence,
    Alert, MaintenanceRecord, FuelRecord, Report, Notification, Contact,
)

admin.site.site_header = 'AutoVehicle Tracker Admin'
admin.site.site_title  = 'AVT Admin'
admin.site.index_title = 'Administration'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'role', 'phone', 'department']
    list_filter   = ['role']
    search_fields = ['user__username', 'user__email']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display  = ['vehicle_number', 'name', 'vehicle_type', 'status', 'fuel_level', 'assigned_driver']
    list_filter   = ['status', 'vehicle_type', 'fuel_type']
    search_fields = ['vehicle_number', 'name', 'make', 'model']


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display  = ['user', 'license_number', 'license_type', 'rating', 'is_available']
    list_filter   = ['license_type', 'is_available']


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'driver', 'start_location', 'end_location', 'status', 'scheduled_start']
    list_filter  = ['status']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'alert_type', 'severity', 'is_read', 'is_resolved', 'created_at']
    list_filter  = ['alert_type', 'severity', 'is_resolved']


@admin.register(MaintenanceRecord)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'service_type', 'scheduled_date', 'status', 'cost']
    list_filter  = ['status', 'service_type']


@admin.register(FuelRecord)
class FuelAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'driver', 'date', 'fuel_quantity', 'fuel_cost']


@admin.register(Geofence)
class GeofenceAdmin(admin.ModelAdmin):
    list_display = ['name', 'radius', 'is_active']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'generated_by', 'created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_read', 'created_at']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_replied', 'created_at']
