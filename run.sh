#!/usr/bin/env bash
set -e

echo ""
echo "  ============================================================="
echo "   AutoVehicle Tracker Pro  |  Setup & Launch"
echo "  ============================================================="
echo ""

# ── Check Python ──────────────────────────────────────────────────────────
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "  [ERROR] Python not found. Install Python 3.10+ and retry."
    exit 1
fi
echo "  [OK] $($PYTHON --version) found"

# ── Install dependencies ──────────────────────────────────────────────────
echo "  [1/5] Installing packages..."
$PYTHON -m pip install --upgrade pip -q
$PYTHON -m pip install Django Pillow django-crispy-forms crispy-bootstrap5 django-widget-tweaks -q
echo "        Done."

# ── Migrations ────────────────────────────────────────────────────────────
echo "  [2/5] Running migrations..."
$PYTHON manage.py makemigrations --noinput
$PYTHON manage.py migrate --noinput
echo "        Done."

# ── Seed data ─────────────────────────────────────────────────────────────
echo "  [3/5] Seeding sample data..."
$PYTHON manage.py seed_data
echo "        Done."

# ── Dirs ──────────────────────────────────────────────────────────────────
echo "  [4/5] Creating media directories..."
mkdir -p media/vehicles media/profiles media/drivers media/reports static
echo "        Done."

echo ""
echo "  ============================================================="
echo "   SUCCESS! Open your browser at:"
echo ""
echo "       http://127.0.0.1:8000"
echo ""
echo "   Login:   admin   / admin123"
echo "   User:    user1   / user123"
echo "   Driver:  driver1 / driver123"
echo "  ============================================================="
echo ""
echo "  [5/5] Starting server... (Ctrl+C to stop)"
echo ""

# Open browser (works on Mac and Linux desktops)
( sleep 2 && (open http://127.0.0.1:8000 2>/dev/null || xdg-open http://127.0.0.1:8000 2>/dev/null || true) ) &

$PYTHON manage.py runserver 127.0.0.1:8000
