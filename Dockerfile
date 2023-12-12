FROM python:3.11.7-alpine

RUN yes | pip install --upgrade pip \
    && yes | pip install --no-cache-dir pipenv

COPY . ./app
WORKDIR /app

RUN pipenv --python 3.11 install --deploy --system

CMD ["python", "-u", "main.py"]
