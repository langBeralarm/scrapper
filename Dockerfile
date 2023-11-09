FROM python:3.11-alpine

RUN yes | pip install --upgrade pip \
    && yes | pip install --no-cache-dir pipenv

COPY . ./app

WORKDIR /app

RUN pipenv install --deploy --system
