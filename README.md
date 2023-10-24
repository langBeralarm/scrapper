# Scrapper
This is a scrap repo for testing out new things in Python.

# Celery
This branch is used for testing and learning [Celery](https://docs.celeryq.dev/en/stable/index.html).

## Run the RabbitMQ message broker
To run the message broker, Docker must be running. Then execute the `start-rabbitmq.sh` script.
```bash
bash start-rabbitmq.sh
```

## Run the Celery Worker
To start the celery worker the module with the application has to specified.
```bash
celery -A scrapper worker -l DEBUG
```
