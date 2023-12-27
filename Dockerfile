# FROM python:3.11.6
FROM python:3.11.6-slim

RUN mkdir -p /usr/src

WORKDIR /usr/src

RUN mv /etc/pip.conf /etc/pip.conf.backup

COPY .devcontainer/pip.conf /etc/pip.conf

COPY requirements.txt ./

RUN pip install -r requirements.txt

RUN mv /etc/pip.conf.backup /etc/pip.conf

COPY /src ./

ENTRYPOINT python manage.py runserver 0.0.0.0:8000