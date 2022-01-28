FROM python:3.9
LABEL MAINTAINER="Pixelfield, s.r.o"

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y dist-upgrade
RUN apt install -y netcat

COPY ./requirements.txt /requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt


RUN mkdir /app
WORKDIR /app
COPY ./app /app
COPY ./scripts /scripts
COPY .env /.env
RUN mkdir /tmp/runtime-user

# collect static files
RUN python manage.py collectstatic --noinput

# add and run as non-root user
# RUN adduser -D myuser
# USER myuser

ENTRYPOINT ["/scripts/server_run.sh"]

