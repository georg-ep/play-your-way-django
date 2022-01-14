#! /bin/sh
echo $IS_DEVELOPMENT
printenv
if [ "$IS_DEVELOPMENT" = "1" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.5
    done

    echo "PostgreSQL started"
    python /app/manage.py migrate
    python /app/manage.py collectstatic --no-input --clear
    python /app/manage.py runserver 0.0.0.0:80
else
    python /app/manage.py migrate
    python /app/manage.py createsuperuser --noinput
    gunicorn --bind 0.0.0.0:80 --workers 1 --threads 8 --timeout 0 wsgi:application
fi
exec "$@"
