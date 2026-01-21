# pull official base image
FROM python:3.13.0-slim-bookworm

# set working directory
WORKDIR /app

# set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./apps/api/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# add logs
RUN mkdir /app/logs
RUN touch /app/logs/celery.log
