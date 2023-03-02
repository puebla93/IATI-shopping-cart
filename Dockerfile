FROM python:3.10.9

ENV PYTHONUNBUFFERED 1

RUN set -ex \
    && apt-get update \
    && apt-get install -y cron \
    && pip install --no-cache-dir pip-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /api
COPY requirements.in requirements-dev.in requirements.txt requirements-dev.txt ./
RUN pip-sync requirements.txt requirements-dev.txt
COPY . .
