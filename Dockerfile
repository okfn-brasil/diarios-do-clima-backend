FROM python:3.9
WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN apt-get install -y python3.9-dev

RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY . .