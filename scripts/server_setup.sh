#! /bin/sh
python ../app/manage.py migrate --noinput --email
python ../app/manage.py collectstatic --noinput --clear --email
python ../app/manage.py createsuperuser --noinput --email