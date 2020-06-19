from python:3.7.7-slim-buster

LABEL maintainer="Nam Khanh Viet-Anh"

# copy application code
ADD functions /opt/fad-functions
WORKDIR /opt/fad-functions

# install env
RUN apt-get -yqq update
RUN apt-get -yqq install curl nano

# install app specific deps
RUN pip3 install -r requirements.txt
