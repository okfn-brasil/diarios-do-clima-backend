FROM docker.io/python:3.8

ARG HOME_DIR=/opt/app
ARG UNAME=diariodoclima

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=$HOME_DIR

RUN useradd --no-log-init --system $UNAME && \
	apt-get update -y && \
  apt-get install -y python3.8-dev wait-for-it

WORKDIR $HOME_DIR

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
