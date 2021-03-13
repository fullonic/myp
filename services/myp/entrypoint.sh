#!/bin/sh
# https://stackoverflow.com/questions/49693148/running-celery-worker-beat-in-the-same-container
echo "Waiting for postgres..."

while ! nc -z myp-db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# Start Celery Workers
echo "STARTING CELERY"
# /usr/bin/supervisord -c /home/myp/app/supervisor_worker.conf --nodaemon &
celery worker -A celery_runner -l info &
echo "STARTING APP"
python manage.py recreate_db &
python manage.py create_folders &
python manage.py run -h 0.0.0.0
