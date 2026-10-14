import json
import random
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Avg, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import (
    LoginForm, RegisterForm, VehicleForm, TripForm, GeofenceForm,
    AlertForm, MaintenanceForm, FuelForm, ReportForm, ContactForm,
    UserProfileForm,
)
from .models import (
    UserProfile, Vehicle, Driver, Trip, Geofence,
    Alert, MaintenanceRecord, FuelRecord, Report, Notification, Contact,
)


# ─── helpers ────────────────────────────────────────────────────────────────

def _is_admin(user):
    try:
        return user.userprofile.role == 'admin'
    except Exception:
        return user.is_superuser


def _get_or_create_profile(user):
    try:
        return user.userprofile
    except UserProfile.DoesNotExist:
        return UserProfile.objects.create(user=user)


# ─── public pages ───────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    stats = {
        'total_vehicles': Vehicle.objects.count(),
        'active_vehicles': Vehicle.objects.filter(status='active').count(),
        'total_trips':    Trip.objects.count(),
        'total_drivers':  Driver.objects.count(),
    }
    return render(request, 'tracker/home.html', {'stats': stats})


def about(request):
    return render(request, 'tracker/about.html')


def features_view(request):
    return render(request, 'tracker/features.html')


def pricing_view(request):
    return render(request, 'tracker/pricing.html')


def contact_view(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your message has been sent! We will reply within 24 hours.')
        return redirect('contact')
    return render(request, 'tracker/contact.html', {'form': form})


# ─── auth ────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'tracker/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        UserProfile.objects.create(
            user=user,
            role=form.cleaned_data.get('role', 'user'),
            phone=form.cleaned_data.get('phone', ''),
        )
        login(request, user)
        messages.success(request, f'Account created! Welcome, {user.first_name or user.username}!')
        return redirect('dashboard')
    return render(request, 'tracker/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


# ─── USER MODULE 1 – Dashboard ───────────────────────────────────────────────

@login_required
def dashboard(request):
    profile = _get_or_create_profile(request.user)
    vehicles = Vehicle.objects.all()
    status_counts = {s: vehicles.filter(status=s).count()
                     for s in ('active', 'idle', 'maintenance', 'offline')}
    chart_data = json.dumps({
        'labels': ['Active', 'Idle', 'Maintenance', 'Offline'],
        'data':   [status_counts['active'], status_counts['idle'],
                   status_counts['maintenance'], status_counts['offline']],
    })
    ctx = {
        'total_vehicles':       vehicles.count(),
        'active_vehicles':      status_counts['active'],
        'idle_vehicles':        status_counts['idle'],
        'maintenance_vehicles': status_counts['maintenance'],
        'total_drivers':        Driver.objects.count(),
        'total_trips':          Trip.objects.count(),
        'ongoing_trips':        Trip.objects.filter(status='ongoing').count(),
        'unread_alerts':        Alert.objects.filter(is_resolved=False).count(),
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
        'recent_alerts':        Alert.objects.filter(is_resolved=False).order_by('-created_at')[:6],
        'recent_trips':         Trip.objects.order_by('-created_at')[:6],
        'is_admin_user':        _is_admin(request.user),
        'chart_data':           chart_data,
        'profile':              profile,
    }
    return render(request, 'tracker/dashboard.html', ctx)


# ─── USER MODULE 2 – Vehicles ────────────────────────────────────────────────

@login_required
def vehicle_list(request):
    qs = Vehicle.objects.all()
    search = request.GET.get('q', '')
    status = request.GET.get('status', '')
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(vehicle_number__icontains=search))
    if status:
        qs = qs.filter(status=status)
    page_obj = Paginator(qs.order_by('vehicle_number'), 10).get_page(request.GET.get('page'))
    return render(request, 'tracker/vehicles/list.html',
                  {'vehicles': page_obj, 'search': search, 'status': status})


@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    ctx = {
        'vehicle':     vehicle,
        'trips':       vehicle.trips.order_by('-created_at')[:10],
        'alerts':      vehicle.alerts.order_by('-created_at')[:10],
        'maintenance': vehicle.maintenance_records.order_by('-scheduled_date')[:6],
        'fuel_recs':   vehicle.fuel_records.order_by('-date')[:10],
    }
    return render(request, 'tracker/vehicles/detail.html', ctx)


# ─── USER MODULE 3 – Live Tracking ───────────────────────────────────────────

@login_required
def live_tracking(request):
    vehicles = Vehicle.objects.exclude(status='offline')
    vdata = []
    for v in vehicles:
        vdata.append({
            'id':     v.id,
            'name':   v.name,
            'number': v.vehicle_number,
            'lat':    v.latitude  + random.uniform(-0.04, 0.04),
            'lng':    v.longitude + random.uniform(-0.04, 0.04),
            'status': v.status,
            'speed':  round(random.uniform(20, 80), 1) if v.status == 'active' else 0,
            'type':   v.vehicle_type,
            'fuel':   v.fuel_level,
        })
    return render(request, 'tracker/tracking/live.html', {
        'vehicles':      vehicles,
        'vehicles_json': json.dumps(vdata),
    })


@login_required
def api_vehicle_locations(request):
    vehicles = Vehicle.objects.exclude(status='offline')
    data = []
    for v in vehicles:
        data.append({
            'id': v.id, 'name': v.name, 'number': v.vehicle_number,
            'lat':  v.latitude  + random.uniform(-0.01, 0.01),
            'lng':  v.longitude + random.uniform(-0.01, 0.01),
            'status': v.status,
            'speed': round(random.uniform(20, 80), 1) if v.status == 'active' else 0,
            'type': v.vehicle_type, 'fuel': v.fuel_level,
        })
    return JsonResponse({'vehicles': data})


# ─── USER MODULE 4 – Trips ───────────────────────────────────────────────────

@login_required
def trip_list(request):
    qs = Trip.objects.all()
    if not _is_admin(request.user):
        qs = qs.filter(Q(driver=request.user) | Q(created_by=request.user))
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)
    page_obj = Paginator(qs.order_by('-created_at'), 10).get_page(request.GET.get('page'))
    return render(request, 'tracker/trips/list.html', {'trips': page_obj, 'status': status})


@login_required
def trip_detail(request, pk):
    return render(request, 'tracker/trips/detail.html', {'trip': get_object_or_404(Trip, pk=pk)})


@login_required
def trip_create(request):
    form = TripForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        t = form.save(commit=False)
        t.created_by = request.user
        t.save()
        messages.success(request, 'Trip scheduled successfully!')
        return redirect('trip_list')
    return render(request, 'tracker/trips/form.html', {'form': form, 'title': 'Schedule New Trip'})


# ─── USER MODULE 5 – Alerts ──────────────────────────────────────────────────

@login_required
def alert_list(request):
    qs = Alert.objects.all()
    sev = request.GET.get('severity', '')
    if sev:
        qs = qs.filter(severity=sev)
    page_obj = Paginator(qs.order_by('-created_at'), 15).get_page(request.GET.get('page'))
    return render(request, 'tracker/alerts/list.html', {
        'alerts':       page_obj,
        'unread_count': Alert.objects.filter(is_read=False).count(),
        'severity':     sev,
    })


@login_required
def alert_mark_read(request, pk):
    a = get_object_or_404(Alert, pk=pk)
    a.is_read = True
    a.save()
    messages.success(request, 'Alert marked as read.')
    return redirect('alert_list')


@login_required
def alert_resolve(request, pk):
    a = get_object_or_404(Alert, pk=pk)
    a.is_resolved = True
    a.resolved_by = request.user
    a.is_read = True
    a.save()
    messages.success(request, 'Alert resolved.')
    return redirect('alert_list')


# ─── USER MODULE 6 – Maintenance ─────────────────────────────────────────────

@login_required
def maintenance_list(request):
    qs = MaintenanceRecord.objects.all().order_by('-scheduled_date')
    page_obj = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'tracker/maintenance/list.html', {'records': page_obj})


# ─── USER MODULE 7 – Fuel ────────────────────────────────────────────────────

@login_required
def fuel_list(request):
    qs = FuelRecord.objects.all().order_by('-date')
    totals = FuelRecord.objects.aggregate(
        total_cost=Sum('fuel_cost'), total_qty=Sum('fuel_quantity')
    )
    page_obj = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'tracker/fuel/list.html', {
        'records':    page_obj,
        'total_cost': totals['total_cost'] or 0,
        'total_qty':  totals['total_qty']  or 0,
    })


@login_required
def fuel_create(request):
    form = FuelForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Fuel record added.')
        return redirect('fuel_list')
    return render(request, 'tracker/fuel/form.html', {'form': form, 'title': 'Add Fuel Record'})


# ─── USER MODULE 8 – Reports ─────────────────────────────────────────────────

@login_required
def report_list(request):
    qs = Report.objects.filter(generated_by=request.user).order_by('-created_at')
    return render(request, 'tracker/reports/list.html', {'reports': qs})


@login_required
def report_create(request):
    form = ReportForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        r = form.save(commit=False)
        r.generated_by = request.user
        r.save()
        messages.success(request, 'Report generated!')
        return redirect('report_list')
    return render(request, 'tracker/reports/form.html', {'form': form, 'title': 'Generate Report'})


# ─── USER MODULE 9 – Notifications ───────────────────────────────────────────

@login_required
def notifications_view(request):
    qs = Notification.objects.filter(user=request.user)
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    page_obj = Paginator(qs, 15).get_page(request.GET.get('page'))
    return render(request, 'tracker/notifications.html', {'notifications': page_obj})


# ─── USER MODULE 10 – Profile ────────────────────────────────────────────────

@login_required
def profile_view(request):
    profile = _get_or_create_profile(request.user)
    form = UserProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name  = request.POST.get('last_name',  request.user.last_name)
        request.user.email      = request.POST.get('email',      request.user.email)
        request.user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'tracker/profile.html', {'form': form, 'profile': profile})


# ─── ADMIN MODULE 1 – Admin Dashboard ────────────────────────────────────────

@login_required
@user_passes_test(_is_admin)
def admin_dashboard(request):
    ctx = {
        'total_users':       User.objects.count(),
        'total_vehicles':    Vehicle.objects.count(),
        'total_drivers':     Driver.objects.count(),
        'total_trips':       Trip.objects.count(),
        'unresolved_alerts': Alert.objects.filter(is_resolved=False).count(),
        'pending_maint':     MaintenanceRecord.objects.filter(status='scheduled').count(),
        'total_fuel_cost':   FuelRecord.objects.aggregate(t=Sum('fuel_cost'))['t'] or 0,
        'new_contacts':      Contact.objects.filter(is_replied=False).count(),
        'recent_users':      User.objects.order_by('-date_joined')[:6],
        'recent_contacts':   Contact.objects.order_by('-created_at')[:5],
    }
    return render(request, 'tracker/admin/dashboard.html', ctx)


# ─── ADMIN MODULE 2 – User Management ────────────────────────────────────────

@login_required
@user_passes_test(_is_admin)
def admin_users(request):
    qs = User.objects.all().order_by('-date_joined')
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(first_name__icontains=q))
    page_obj = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'tracker/admin/users.html', {'users': page_obj, 'q': q})


@login_required
@user_passes_test(_is_admin)
def admin_user_toggle(request, pk):
    u = get_object_or_404(User, pk=pk)
    if u == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('admin_users')
    u.is_active = not u.is_active
    u.save()
    messages.success(request, f'User {u.username} {"activated" if u.is_active else "deactivated"}.')
    return redirect('admin_users')


# ─── ADMIN MODULE 3 – Vehicle Management ─────────────────────────────────────

@login_required
@user_passes_test(_is_admin)
def admin_vehicles(request):
    vehicles = Vehicle.objects.all().order_by('vehicle_number')
    return render(request, 'tracker/admin/vehicles.html', {'vehicles': vehicles})


@login_required
@user_passes_test(_is_admin)
def vehicle_create(request):
    form = VehicleForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Vehicle added!')
        return redirect('admin_vehicles')
    return render(request, 'tracker/vehicles/form.html', {'form': form, 'title': 'Add Vehicle'})


@login_required
@user_passes_test(_is_admin)
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    form = VehicleForm(request.POST or None, request.FILES or None, instance=vehicle)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Vehicle updated!')
        return redirect('admin_vehicles')
    return render(request, 'tracker/vehicles/form.html', {'form': form, 'title': 'Edit Vehicle', 'vehicle': vehicle})


@login_required
@user_passes_test(_is_admin)
def vehicle_delete(request, pk):
    get_object_or_404(Vehicle, pk=pk).delete()
    messages.success(request, 'Vehicle deleted.')
    return redirect('admin_vehicles')


# ─── ADMIN MODULE 4 – Driver Management ──────────────────────────────────────

@login_required
@user_passes_test(_is_admin)
def admin_drivers(request):
    drivers = Driver.objects.select_related('user').all()
    return render(request, 'tracker/admin/drivers.html', {'drivers': drivers})


# ─── ADMIN MODULE 5 – Trip Management ────────────────────────────────────────

@login_required
@user_passes_test(_is_admin)
def admin_trips(request):
    qs = Trip.objects.all()
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)
    page_obj = Paginator(qs.order_by('-created_at'), 10).get_page(request.GET.get('page'))
    return render(request, 'tracker/admin/trips.html', {'trips': page_obj, 'status': status})


# ─── ADMIN MODULE 6 – Alert Management ───────────────────────────────────────

@login_required
@user_passes_test(_is_admin)
def admin_alerts(request):
    form = AlertForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Alert created.')
        return redirect('admin_alerts')
    qs = Alert.objects.all().order_by('-created_at')
    page_obj = Paginator(qs, 15).get_page(request.GET.get('page'))
    return render(request, 'tracker/admin/alerts.html', {'alerts': page_obj, 'form': form})


# ─── ADMIN MODULE 7 – Geofence Management ────────────────────────────────────

@login_required
@user_passes_test(_is_admin)
def admin_geofences(request):
    form = GeofenceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        g = form.save(commit=False)
        g.created_by = request.user
        g.save()
        form.save_m2m()
        messages.success(request, 'Geofence created.')
        return redirect('admin_geofences')
    geofences = Geofence.objects.all()
    return render(request, 'tracker/admin/geofences.html', {'geofences': geofences, 'form': form})


# ─── ADMIN MODULE 8 – Maintenance Management ─────────────────────────────────

@login_required
@user_passes_test(_is_admin)
def admin_maintenance(request):
    form = MaintenanceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        r = form.save(commit=False)
        r.created_by = request.user
        r.save()
        messages.success(request, 'Record added.')
        return redirect('admin_maintenance')
    qs = MaintenanceRecord.objects.all().order_by('-scheduled_date')
    page_obj = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'tracker/admin/maintenance.html', {'records': page_obj, 'form': form})


# ─── ADMIN MODULE 9 – Fuel Management ────────────────────────────────────────

@login_required
@user_passes_test(_is_admin)
def admin_fuel(request):
    qs = FuelRecord.objects.all().order_by('-date')
    totals = FuelRecord.objects.aggregate(
        total_cost=Sum('fuel_cost'), total_qty=Sum('fuel_quantity'), avg_cost=Avg('fuel_cost')
    )
    page_obj = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'tracker/admin/fuel.html', {
        'records':    page_obj,
        'total_cost': totals['total_cost'] or 0,
        'total_qty':  totals['total_qty']  or 0,
        'avg_cost':   totals['avg_cost']   or 0,
    })


# ─── ADMIN MODULE 10 – Contact Management ────────────────────────────────────

@login_required
@user_passes_test(_is_admin)
def admin_contacts(request):
    contacts  = Contact.objects.all().order_by('-created_at')
    unreplied = contacts.filter(is_replied=False).count()
    return render(request, 'tracker/admin/contacts.html', {'contacts': contacts, 'unreplied': unreplied})


@login_required
@user_passes_test(_is_admin)
def admin_contact_reply(request, pk):
    c = get_object_or_404(Contact, pk=pk)
    c.is_replied = True
    c.save()
    messages.success(request, 'Marked as replied.')
    return redirect('admin_contacts')


# ─── Admin: Reports list ──────────────────────────────────────────────────────

@login_required
@user_passes_test(_is_admin)
def admin_reports(request):
    reports = Report.objects.all().order_by('-created_at')
    return render(request, 'tracker/admin/reports.html', {'reports': reports})
