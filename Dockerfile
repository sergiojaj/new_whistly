# Pull base image
FROM python:3.12-slim

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work dir
WORKDIR /code

# Install dependencies
COPY Pipfile Pipfile.lock /code/
RUN pip install -U pip pipenv && pipenv install --system --deploy

# Copy project
COPY . /code/
