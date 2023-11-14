FROM python:3.11-alpine

RUN yes | pip install --upgrade pip \
    && yes | pip install --no-cache-dir pipenv

COPY . ./app

# Add non-root user
RUN adduser developer;echo 'developer:pass' | chpasswd

WORKDIR /app

RUN pipenv install --deploy --system
