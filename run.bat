@echo off
title AutoVehicle Tracker Pro - Setup and Launch
color 0A
cls

echo.
echo  =============================================================
echo    AutoVehicle Tracker Pro  ^|  Setup ^& Launch
echo  =============================================================
echo.

:: ── Check Python ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found!
    echo  Please install Python 3.10+ from https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo  [OK] %%i found

:: ── Install dependencies ───────────────────────────────────────────────────
echo.
echo  [1/5] Installing Python packages...
python -m pip install --upgrade pip --quiet
python -m pip install Django Pillow django-crispy-forms crispy-bootstrap5 django-widget-tweaks --quiet
if errorlevel 1 (
    echo  [ERROR] Package install failed. Check your internet connection.
    pause
    exit /b 1
)
echo        Done.

:: ── Database migrations ────────────────────────────────────────────────────
echo  [2/5] Running database migrations...
python manage.py makemigrations --noinput
python manage.py migrate --noinput
if errorlevel 1 (
    echo  [ERROR] Migration failed.
    pause
    exit /b 1
)
echo        Done.

:: ── Seed sample data ───────────────────────────────────────────────────────
echo  [3/5] Seeding sample data...
python manage.py seed_data
echo        Done.

:: ── Static / media dirs ────────────────────────────────────────────────────
echo  [4/5] Creating media directories...
if not exist "media\vehicles"  mkdir media\vehicles
if not exist "media\profiles"  mkdir media\profiles
if not exist "media\drivers"   mkdir media\drivers
if not exist "media\reports"   mkdir media\reports
if not exist "static"          mkdir static
echo        Done.

:: ── Launch ────────────────────────────────────────────────────────────────
echo  [5/5] Starting development server...
echo.
echo  =============================================================
echo   SUCCESS! Open your browser at:
echo.
echo       http://127.0.0.1:8000
echo.
echo   Login:   admin   / admin123
echo   User:    user1   / user123
echo   Driver:  driver1 / driver123
echo  =============================================================
echo.
echo  Press Ctrl+C to stop the server.
echo.

:: Open browser after 2 seconds
ping 127.0.0.1 -n 3 >nul
start http://127.0.0.1:8000

python manage.py runserver 127.0.0.1:8000
pause
