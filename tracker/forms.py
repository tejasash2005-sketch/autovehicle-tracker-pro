from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import (
    UserProfile, Vehicle, Driver, Trip, Geofence,
    Alert, MaintenanceRecord, FuelRecord, Report, Contact
)

W = {'class': 'form-control'}
WS = {'class': 'form-select'}


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={**W, 'placeholder': 'Username', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={**W, 'placeholder': 'Password', 'id': 'id_password'}))


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={**W, 'placeholder': 'First Name'}))
    last_name  = forms.CharField(max_length=100, widget=forms.TextInput(attrs={**W, 'placeholder': 'Last Name'}))
    email      = forms.EmailField(widget=forms.EmailInput(attrs={**W, 'placeholder': 'Email'}))
    phone      = forms.CharField(max_length=15,  widget=forms.TextInput(attrs={**W, 'placeholder': 'Phone'}))
    role       = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, widget=forms.Select(attrs=WS))

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {'username': forms.TextInput(attrs={**W, 'placeholder': 'Username'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={**W, 'placeholder': 'Password'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={**W, 'placeholder': 'Confirm Password'})


class VehicleForm(forms.ModelForm):
    class Meta:
        model  = Vehicle
        exclude = ['created_at', 'updated_at', 'latitude', 'longitude', 'speed']
        widgets = {
            'name':                forms.TextInput(attrs=W),
            'vehicle_number':      forms.TextInput(attrs=W),
            'vehicle_type':        forms.Select(attrs=WS),
            'make':                forms.TextInput(attrs=W),
            'model':               forms.TextInput(attrs=W),
            'year':                forms.NumberInput(attrs=W),
            'color':               forms.TextInput(attrs=W),
            'fuel_type':           forms.Select(attrs=WS),
            'status':              forms.Select(attrs=WS),
            'assigned_driver':     forms.Select(attrs=WS),
            'fuel_level':          forms.NumberInput(attrs=W),
            'mileage':             forms.NumberInput(attrs=W),
            'insurance_expiry':    forms.DateInput(attrs={**W, 'type': 'date'}),
            'registration_expiry': forms.DateInput(attrs={**W, 'type': 'date'}),
            'last_service_date':   forms.DateInput(attrs={**W, 'type': 'date'}),
            'image':               forms.FileInput(attrs=W),
        }


class TripForm(forms.ModelForm):
    class Meta:
        model   = Trip
        exclude = ['created_at', 'actual_start', 'actual_end', 'created_by', 'distance_km', 'fuel_consumed']
        widgets = {
            'vehicle':         forms.Select(attrs=WS),
            'driver':          forms.Select(attrs=WS),
            'start_location':  forms.TextInput(attrs=W),
            'end_location':    forms.TextInput(attrs=W),
            'scheduled_start': forms.DateTimeInput(attrs={**W, 'type': 'datetime-local'}),
            'status':          forms.Select(attrs=WS),
            'purpose':         forms.TextInput(attrs=W),
            'notes':           forms.Textarea(attrs={**W, 'rows': 3}),
        }


class GeofenceForm(forms.ModelForm):
    class Meta:
        model   = Geofence
        exclude = ['created_at', 'created_by']
        widgets = {
            'name':             forms.TextInput(attrs=W),
            'description':      forms.Textarea(attrs={**W, 'rows': 3}),
            'center_latitude':  forms.NumberInput(attrs={**W, 'step': 'any'}),
            'center_longitude': forms.NumberInput(attrs={**W, 'step': 'any'}),
            'radius':           forms.NumberInput(attrs=W),
            'vehicles':         forms.SelectMultiple(attrs=W),
        }


class AlertForm(forms.ModelForm):
    class Meta:
        model   = Alert
        exclude = ['created_at', 'is_read', 'resolved_by', 'latitude', 'longitude']
        widgets = {
            'vehicle':    forms.Select(attrs=WS),
            'alert_type': forms.Select(attrs=WS),
            'severity':   forms.Select(attrs=WS),
            'message':    forms.Textarea(attrs={**W, 'rows': 3}),
        }


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model   = MaintenanceRecord
        exclude = ['created_at', 'created_by']
        widgets = {
            'vehicle':             forms.Select(attrs=WS),
            'service_type':        forms.Select(attrs=WS),
            'service_center':      forms.TextInput(attrs=W),
            'scheduled_date':      forms.DateInput(attrs={**W, 'type': 'date'}),
            'completed_date':      forms.DateInput(attrs={**W, 'type': 'date'}),
            'cost':                forms.NumberInput(attrs=W),
            'mileage_at_service':  forms.NumberInput(attrs=W),
            'status':              forms.Select(attrs=WS),
            'technician_name':     forms.TextInput(attrs=W),
            'description':         forms.Textarea(attrs={**W, 'rows': 3}),
            'next_service_due':    forms.DateInput(attrs={**W, 'type': 'date'}),
            'next_service_mileage':forms.NumberInput(attrs=W),
        }


class FuelForm(forms.ModelForm):
    class Meta:
        model   = FuelRecord
        exclude = ['created_at']
        widgets = {
            'vehicle':       forms.Select(attrs=WS),
            'driver':        forms.Select(attrs=WS),
            'date':          forms.DateTimeInput(attrs={**W, 'type': 'datetime-local'}),
            'fuel_quantity': forms.NumberInput(attrs={**W, 'step': '0.01'}),
            'fuel_cost':     forms.NumberInput(attrs={**W, 'step': '0.01'}),
            'mileage_at_fill':forms.NumberInput(attrs=W),
            'station_name':  forms.TextInput(attrs=W),
            'receipt_number':forms.TextInput(attrs=W),
            'notes':         forms.Textarea(attrs={**W, 'rows': 2}),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model  = Report
        fields = ['name', 'report_type', 'vehicle', 'start_date', 'end_date']
        widgets = {
            'name':        forms.TextInput(attrs=W),
            'report_type': forms.Select(attrs=WS),
            'vehicle':     forms.Select(attrs=WS),
            'start_date':  forms.DateInput(attrs={**W, 'type': 'date'}),
            'end_date':    forms.DateInput(attrs={**W, 'type': 'date'}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model  = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name':    forms.TextInput(attrs={**W, 'placeholder': 'Your Name'}),
            'email':   forms.EmailInput(attrs={**W, 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={**W, 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={**W, 'placeholder': 'Your message…', 'rows': 5}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model  = UserProfile
        fields = ['phone', 'address', 'profile_pic', 'department', 'employee_id']
        widgets = {
            'phone':       forms.TextInput(attrs=W),
            'address':     forms.Textarea(attrs={**W, 'rows': 3}),
            'profile_pic': forms.FileInput(attrs=W),
            'department':  forms.TextInput(attrs=W),
            'employee_id': forms.TextInput(attrs=W),
        }
