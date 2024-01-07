FROM python:3.11.6

RUN mkdir -p /usr/src

WORKDIR /usr/src

COPY .autodevops/.build/pip.conf /root/.config/pip/

COPY requirements.txt requirements_dev.txt ./
RUN cat requirements.txt requirements_dev.txt > requirements_install.txt

RUN pip install -r requirements_install.txt