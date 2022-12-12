#!/bin/sh


python manage.py makemihrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input


gunicorn wazieat_admin.wsgi:application --bind 0.0.0.0:8000
