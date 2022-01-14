# Django Rest framework skeleton app

## Content: ##

1. Quick start setup
2. Manual setup
3. Features

## Quick start setup: ##

1. Setup env variables for local development:

   cp env.local.example .env

2. Setup docker-compose override file for local development:

   cp example.docker-compose.override.yml docker-compose.override.yml

3. Run dockerized server:

   docker-compose up

4. After docker image is built and server started, setup migrations/static files/admin access:

   docker-compose exec app sh /scripts/server_setup.sh

## Manual setup ##

1. Set .env variables (see comments in env.dev.example and env.local.example for details):
    1. Create .env file from development (env.dev.example) template
    2. Set PROJECT_NAME, FRONTEND_URL
    3. Set remote DB credentials
    4. Create and copy GC credentials file to GOOGLE_APPLICATION_CREDENTIALS path
    5. Create buckets for static and media files and set fields GS_STATIC_BUCKET_NAME, GS_MEDIA_BUCKET_NAME
    6. Set admin credentials for script or setup them manually later
2. Set docker-compose.override.yml file:
    1. By default all non-core services (db, celery server) are placed remotely, in this case no
       docker-compose.override.yml is needed
    2. To place some services locally add docker-compose.override.yml
3. Run dockerized server: docker-compose up
4. After docker image is built and server started, setup migrations/static files/admin access:
    1. Run 
       
       docker-compose exec app sh /scripts/server_setup.sh for automatic setup 
       
       OR
    2. Apply DB migrations: 
       
       docker-compose exec app python manage.py migrate
       
    3. Setup static files: 
       
       docker-compose exec app python manage.py collectstatic
       
    4. Create superuser for admin access: 
       
       docker-compose exec app python manage.py createsuperuser
   
   
## Features ##

1. Server is served at http://localhost:80
2. Swagger docs are served at http://localhost/docs/all and http://localhost/docs/{app name}
3. Admin panel is served at http://localhost/admin
4. Includes Celery for scheduled and background tasks. See app/core/tasks.py and app/settings.py for examples