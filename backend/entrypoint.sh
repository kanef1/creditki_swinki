#!/bin/sh
set -e

echo "Starting Alfa-Bank Credit Portal Backend Entrypoint..."

# Wait for PostgreSQL if DB_HOST is set
if [ -n "$DB_HOST" ]; then
  echo "Waiting for database on $DB_HOST:${DB_PORT:-5432}..."
  python << 'EOF'
import socket
import time
import os

host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))
timeout = 60
start = time.time()

while True:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"Database connection established on {host}:{port}.")
            break
    except OSError:
        if time.time() - start > timeout:
            print(f"Error: Database connection timeout on {host}:{port}.")
            exit(1)
        print(f"Database not ready yet, retrying in 1s...")
        time.sleep(1)
EOF
fi

echo "Applying Django migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Seeding hackathon demo data (Scenarios A, B, C, D)..."
python manage.py seed_demo_data

echo "Backend initialization complete. Starting server..."
exec "$@"
