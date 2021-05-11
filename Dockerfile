FROM python:3.7.7-slim-buster

LABEL maintainer="Nam Khanh Viet-Anh"
RUN apt-get -yqq update && apt-get -yqq install curl nano procps "wait-for-it"

# copy application code
COPY requirements.txt /opt/fad-functions/requirements.txt
RUN pip3 install -r /opt/fad-functions/requirements.txt
ADD functions /opt/fad-functions
WORKDIR /opt/fad-functions
RUN chmod 755 /opt/fad-functions/celery_run_cmd.sh

# make dirs
RUN mkdir -p /opt/fad-functions/run/celery && mkdir -p /opt/fad-functions/run/scrapy && mkdir -p /opt/fad-functions/logs
RUN rm -f /opt/fad-functions/.env
