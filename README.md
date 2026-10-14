# AutoVehicle Tracker Pro

Full-stack Django fleet management and GPS tracking system.

## Quick Start

### Windows
```
Double-click  run.bat
```

### Linux / Mac
```bash
chmod +x run.sh
./run.sh
```

### Manual
```bash
pip install Django Pillow django-crispy-forms crispy-bootstrap5 django-widget-tweaks
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Open: **http://127.0.0.1:8000**

## Login Credentials

| Role    | Username | Password   |
|---------|----------|------------|
| Admin   | admin    | admin123   |
| User    | user1    | user123    |
| Manager | user2    | user123    |
| Driver  | driver1  | driver123  |

## User Modules (10)
1. Dashboard  
2. Vehicles  
3. Live Tracking (Leaflet.js map)  
4. Trips  
5. Alerts  
6. Maintenance  
7. Fuel Records  
8. Reports  
9. Notifications  
10. Profile  

## Admin Modules (10)
1. Admin Dashboard  
2. User Management  
3. Vehicle Management  
4. Driver Management  
5. Trip Management  
6. Alert Management  
7. Geofence Management  
8. Maintenance Management  
9. Fuel Management  
10. Contact Messages  

## Public Pages
Home, Features, Pricing, About, Contact — all with Login/Register buttons in topbar.
