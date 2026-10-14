# 🚗 AutoVehicle Tracker Pro

A full-stack **fleet management and GPS vehicle tracking system** built with Django. It combines a public marketing site, a role-based user portal, and a complete admin panel for managing vehicles, drivers, trips, alerts, geofences, maintenance and fuel.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet.js-Maps-199900?logo=leaflet&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)

## ✨ Features

- **Live tracking** – real-time vehicle positions on an interactive Leaflet.js map
- **Fleet management** – vehicles, drivers, trips with full detail pages
- **Alerts & geofencing** – create geofences, raise, read and resolve alerts
- **Maintenance & fuel** – service history and fuel consumption records
- **Reports & notifications** – generate reports, in-app notification center
- **Role-based access** – Admin, Manager, User and Driver roles
- **Admin panel** – 10 dedicated management modules
- **Public site** – Home, Features, Pricing, About, Contact, Login and Register
- **Sample data** – one command seeds users, vehicles, trips, alerts and more

## 🧰 Tech Stack

| Layer     | Technology                                              |
|-----------|---------------------------------------------------------|
| Backend   | Django 4.2, Python 3.10+                                |
| Database  | SQLite (default, easy to swap for PostgreSQL/MySQL)     |
| Frontend  | Django templates, Bootstrap 5, Leaflet.js               |
| Forms     | django-crispy-forms, crispy-bootstrap5, widget-tweaks   |
| Media     | Pillow (vehicle, driver and profile images)             |

## 🚀 Getting Started

### Quick start

**Windows:** double-click `run.bat`

**Linux / macOS:**
```bash
chmod +x run.sh
./run.sh
```

The script installs dependencies, runs migrations, seeds sample data and starts the server.

### Manual setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/autovehicle-tracker-pro.git
cd autovehicle-tracker-pro

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up the database
python manage.py makemigrations tracker
python manage.py migrate

# 5. Load sample data
python manage.py seed_data

# 6. Run the server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

## 🔑 Demo Credentials

| Role    | Username  | Password    |
|---------|-----------|-------------|
| Admin   | `admin`   | `admin123`  |
| User    | `user1`   | `user123`   |
| Manager | `user2`   | `user123`   |
| Driver  | `driver1` | `driver123` |

> ⚠️ These are demo accounts created by `seed_data`. Remove or change them before any real deployment.

## 📦 Modules

**User portal (10):** Dashboard · Vehicles · Live Tracking · Trips · Alerts · Maintenance · Fuel Records · Reports · Notifications · Profile

**Admin panel (10):** Dashboard · Users · Vehicles · Drivers · Trips · Alerts · Geofences · Maintenance · Fuel · Contact Messages

## 📁 Project Structure

```
├── manage.py
├── requirements.txt
├── run.sh / run.bat              # one-click setup scripts
├── vehicle_tracker/              # project settings, urls, wsgi
└── tracker/                      # main app
    ├── models.py                 # UserProfile, Vehicle, Driver, Trip, Geofence,
    │                             # Alert, MaintenanceRecord, FuelRecord,
    │                             # Report, Notification, Contact
    ├── views.py / urls.py / forms.py / admin.py
    ├── management/commands/seed_data.py
    └── templates/tracker/        # public, user, and admin-panel templates
```

## 🔌 API

| Endpoint                      | Description                          |
|-------------------------------|--------------------------------------|
| `GET /api/vehicle-locations/` | Current vehicle positions (for map)  |

## 🔒 Before Deploying to Production

- Move `SECRET_KEY` to an environment variable and generate a new one
- Set `DEBUG = False` and restrict `ALLOWED_HOSTS`
- Remove the seeded demo accounts
- Switch to PostgreSQL/MySQL and serve with Gunicorn + Nginx
- Run `python manage.py collectstatic`

## 🛣️ Roadmap

- [ ] Real GPS device / MQTT integration
- [ ] REST API with token authentication
- [ ] Email and SMS alerts
- [ ] Docker setup

## 📄 License

Released under the [MIT License](LICENSE).
