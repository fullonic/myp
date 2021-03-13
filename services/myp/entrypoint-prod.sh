#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z myp-db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# Start Celery Workers
echo "STARTING CELERY"
celery worker -A celery_runner -l info &
echo "STARTING APP"
python manage.py create_db &
python manage.py create_folders &
gunicorn -b 0.0.0.0:5000 manage:app
