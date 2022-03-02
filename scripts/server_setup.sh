#! /bin/sh
python ../app/manage.py migrate 
python ../app/manage.py createsuperuser --email 'admin@admin.com' --noinput