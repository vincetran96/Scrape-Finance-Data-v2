# Base image
FROM python:3.7.7-slim-buster

# Install essential packages to the base image
RUN apt-get -yqq update && apt-get -yqq install curl nano procps "wait-for-it"

# Copy application code
COPY requirements.txt /opt/functions_vietstock/requirements.txt
RUN pip3 install -r /opt/functions_vietstock/requirements.txt
ADD functions_vietstock /opt/functions_vietstock
WORKDIR /opt/functions_vietstock
RUN chmod 755 /opt/functions_vietstock/celery_run_cmd.sh

# Make dirs
RUN mkdir -p /opt/functions_vietstock/run/celery && mkdir -p /opt/functions_vietstock/run/scrapy && mkdir -p /opt/functions_vietstock/logs
RUN rm -f /opt/functions_vietstock/.env
