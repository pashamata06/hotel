#!/bin/sh

python manage.py migrate --noinput
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

exec gunicorn hotel_project.wsgi:application --bind 0.0.0.0:8000
