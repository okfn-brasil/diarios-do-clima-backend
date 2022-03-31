FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /opt/app

RUN python -m pip install --upgrade pip
RUN python -m pip install --upgrade setuptools

COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

COPY . .