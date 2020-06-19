from python:3.7.7-slim-buster

LABEL maintainer="Nam Khanh Viet-Anh"

# copy application code
ADD functions /opt/fad-functions
WORKDIR /opt/fad-functions

# install env, packages and make dir
RUN apt-get -yqq update
RUN apt-get -yqq install curl nano
RUN mkdir -p /opt/fad-functions/run/celery
RUN mkdir -p /opt/fad-functions/logs

# install app specific deps
RUN pip3 install -r requirements.txt
