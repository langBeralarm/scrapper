<p align="center">
    <a href="https://coveralls.io/github/langBeralarm/scrapper?branch=feature/implement-celery"><img src="https://coveralls.io/repos/github/langBeralarm/scrapper/badge.svg?branch=feature/implement-celery" alt="Coverage Status"></a>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

# Scrapper
This is a scrap repo for testing out new things in Python.

## Coveralls
To prevent the job from failing if the coverage decreased the Repo Setting for the Pull Requests Alerts
- `Coverage Threshold for Failure` and
- `Coverage Decrease Threshold for Failure`
need to be set accordingly.

## Usage
To start the application with RabbitMQ as the broker:
```bash
docker-compose up -d
```

To start the application with Redis as the broker:
```bash
docker-compose -f docker-compose.redis.yaml up -d
```
