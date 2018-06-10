FROM python:3.7.0b4-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH $PYTHONPATH:src
ARG DJANGO_ENV

RUN apt update && apt-get install -y \
    libffi-dev \
    gettext \
    git \
    python3-dev \
    libpq-dev \
    gcc \
    python3-psycopg2 \
    libmaxminddb0 libmaxminddb-dev mmdb-bin


WORKDIR /code

COPY requirements/ requirements/

RUN pip install --upgrade pip \
	&& pip install -r requirements/$DJANGO_ENV.txt

COPY . /code/

RUN rm requirements/ -rf \
    && mv docker/django/uwsgi.ini uwsgi.ini \
    && rm docker/ -rf

RUN adduser --disabled-password --gecos '' django \
    && chown -R django /code \
    && mkdir /static \
    && chown -R django /static

USER django

ENV PYTHONPATH $PYTHONPATH:src
CMD uwsgi --ini=./uwsgi.ini
