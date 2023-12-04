# FROM python:3.11.6
FROM python:3.11.6-slim

RUN mkdir -p /usr/src

WORKDIR /usr/src

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY /src ./

ENTRYPOINT python manage.py runserver 0.0.0.0:8000