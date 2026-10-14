from django.urls import path
from . import views

urlpatterns = [
    # ── public ──────────────────────────────────────────────────────────
    path('',            views.home,          name='home'),
    path('about/',      views.about,         name='about'),
    path('features/',   views.features_view, name='features'),
    path('pricing/',    views.pricing_view,  name='pricing'),
    path('contact/',    views.contact_view,  name='contact'),

    # ── auth ──────────────────────────────────────────────────────────
    path('login/',    views.login_view,    name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/',   views.logout_view,   name='logout'),

    # ── USER modules ──────────────────────────────────────────────────
    path('dashboard/',                views.dashboard,        name='dashboard'),
    path('vehicles/',                 views.vehicle_list,     name='vehicle_list'),
    path('vehicles/<int:pk>/',        views.vehicle_detail,   name='vehicle_detail'),
    path('tracking/',                 views.live_tracking,    name='live_tracking'),
    path('trips/',                    views.trip_list,        name='trip_list'),
    path('trips/create/',             views.trip_create,      name='trip_create'),
    path('trips/<int:pk>/',           views.trip_detail,      name='trip_detail'),
    path('alerts/',                   views.alert_list,       name='alert_list'),
    path('alerts/<int:pk>/read/',     views.alert_mark_read,  name='alert_mark_read'),
    path('alerts/<int:pk>/resolve/',  views.alert_resolve,    name='alert_resolve'),
    path('maintenance/',              views.maintenance_list, name='maintenance_list'),
    path('fuel/',                     views.fuel_list,        name='fuel_list'),
    path('fuel/add/',                 views.fuel_create,      name='fuel_create'),
    path('reports/',                  views.report_list,      name='report_list'),
    path('reports/create/',           views.report_create,    name='report_create'),
    path('notifications/',            views.notifications_view, name='notifications'),
    path('profile/',                  views.profile_view,     name='profile'),

    # ── ADMIN modules ─────────────────────────────────────────────────
    path('admin-panel/',                            views.admin_dashboard,      name='admin_dashboard'),
    path('admin-panel/users/',                      views.admin_users,          name='admin_users'),
    path('admin-panel/users/<int:pk>/toggle/',      views.admin_user_toggle,    name='admin_user_toggle'),
    path('admin-panel/vehicles/',                   views.admin_vehicles,       name='admin_vehicles'),
    path('admin-panel/vehicles/add/',               views.vehicle_create,       name='vehicle_create'),
    path('admin-panel/vehicles/<int:pk>/edit/',     views.vehicle_edit,         name='vehicle_edit'),
    path('admin-panel/vehicles/<int:pk>/delete/',   views.vehicle_delete,       name='vehicle_delete'),
    path('admin-panel/drivers/',                    views.admin_drivers,        name='admin_drivers'),
    path('admin-panel/trips/',                      views.admin_trips,          name='admin_trips'),
    path('admin-panel/alerts/',                     views.admin_alerts,         name='admin_alerts'),
    path('admin-panel/geofences/',                  views.admin_geofences,      name='admin_geofences'),
    path('admin-panel/maintenance/',                views.admin_maintenance,    name='admin_maintenance'),
    path('admin-panel/fuel/',                       views.admin_fuel,           name='admin_fuel'),
    path('admin-panel/reports/',                    views.admin_reports,        name='admin_reports'),
    path('admin-panel/contacts/',                   views.admin_contacts,       name='admin_contacts'),
    path('admin-panel/contacts/<int:pk>/reply/',    views.admin_contact_reply,  name='admin_contact_reply'),

    # ── API ───────────────────────────────────────────────────────────
    path('api/vehicle-locations/', views.api_vehicle_locations, name='api_vehicle_locations'),
]
