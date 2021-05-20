# A standalone package to scrape financial data of Vietnamese listed companies via Vietstock.

As this repo is under heavy re-development, so documentation is minimal at the moment.

# Run automatically using Docker
To run, use `docker-compose build --no-cache && docker-compose up`

# Run manually
## Specify a local environment variables
At `functions_vietstock` folder, create a file named `.env` with the following content:
```
REDIS_HOST=localhost
PROXY=yes
TORPROXY_HOST=localhost
```

## Run Redis and Torproxy
```
docker run -d -p 6379:6379 --rm --name scraper-redis redis

docker run -it -d -p 8118:8118 -p 9050:9050 --rm --name torproxy --env TOR_NewCircuitPeriod=10 --env TOR_MaxCircuitDirtiness=60 dperson/torproxy
```
## Clear all previous running files (if any)
```
ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9
pkill -9 -f 'celery worker'
redis-cli flushall
rm -v ./run/celery/*
rm -v ./run/scrapy/*
rm -v ./logs/*
rm -rf ./localData/*
rm -rf ./schemaData/*
```

## Run Celery workers
```
celery -A celery_main worker -Q corpAZ -c 10 -n workercorpAZ@%h -l INFO --pidfile="./run/celery/%n.pid" --detach

celery -A celery_main worker -Q finance -c 10 -n workerfinance@%h -l INFO --pidfile="./run/celery/%n.pid" --detach
```
