from python:3.7.7-slim-buster

LABEL maintainer="Nam Khanh Viet-Anh"

# copy application code
ADD functions /opt/fad-functions
WORKDIR /opt/fad-functions

# install env, packages and make dir
RUN apt-get -yqq update
RUN apt-get -yqq install curl nano procps
RUN mkdir -p /opt/fad-functions/run/celery
RUN mkdir -p /opt/fad-functions/logs
RUN rm -f /opt/fad-functions/.env

# install app specific deps
RUN pip3 install -r requirements.txt
RUN chmod a+x /opt/fad-functions/celery_run_cmd.sh
