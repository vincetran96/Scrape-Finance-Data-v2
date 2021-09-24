# Base image
FROM python:3.8.11-slim-buster

# Install essential packages to the base image
RUN apt-get -y update && apt-get -y install curl nano procps redis-tools "wait-for-it"

# Copy application code
COPY requirements.txt /opt/functions_vietstock/requirements.txt
RUN pip3 install -r /opt/functions_vietstock/requirements.txt
COPY functions_vietstock /opt/functions_vietstock
WORKDIR /opt/functions_vietstock
RUN chmod 755 /opt/functions_vietstock/celery_stop.sh
RUN chmod 755 /opt/functions_vietstock/userinput.sh

# Make dirs and clear .env file
RUN mkdir -p /opt/functions_vietstock/run/celery && mkdir -p /opt/functions_vietstock/run/scrapy && mkdir -p /opt/functions_vietstock/logs
# RUN rm -f /opt/functions_vietstock/.env
