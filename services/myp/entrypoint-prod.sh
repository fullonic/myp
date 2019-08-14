#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z myp-db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# RUNS FLASK SERVER
# python manage.py run -h 0.0.0.0
gunicorn -b 0.0.0.0:5000 manage:app
