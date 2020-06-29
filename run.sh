#!/bin/bash

# stop any running docker-compose
docker-compose down -v

# delete all logs, running files
rm -v ./functions/run/celery/*
rm -v ./functions/run/scrapy/*
rm -v ./functions/logs/*
rm -rf ./functions/localData/*

# run docker-compose
docker-compose up
