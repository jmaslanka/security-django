FROM python:3.7.0b4-alpine3.7

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH $PYTHONPATH:src
ARG DJANGO_ENV

RUN apk update
RUN apk add \
    build-base \
    zlib-dev \
    jpeg-dev \
    python3-dev \
    py3-psycopg2 \
    libressl-dev \
    libffi-dev \
    postgresql-dev \
    linux-headers

WORKDIR /code

COPY requirements/ requirements/

RUN pip install --upgrade pip \
	&& pip install -r requirements/$DJANGO_ENV.txt

COPY . /code/

RUN rm requirements/ -rf \
    && mv docker/django/uwsgi.ini uwsgi.ini \
    && rm docker/ -rf

RUN addgroup -S django \
    && adduser -S -G django django \
    && chown -R django:django /code \
    && mkdir media static \
    && chown -R django:django media \
    && chown -R django:django static

USER django

CMD uwsgi --ini=./uwsgi.ini
