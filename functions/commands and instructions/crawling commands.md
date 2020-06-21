# Requirements outside of pip
redis
tor
privoxy

# Create directories
localData/associates
localData/boardDetails
localData/financeInfo
localData/majorShareholders
localData/ownerStructure
localData/PDFs
logs

# Run redis
redis-server

# Run rabbitmq broker
rabbitmq

# Start a celery worker
celery -A celery_main worker -l INFO --detach
celery -A celery_main worker -Q corpAZ -c 10 -n workercorpAZ@%h -l INFO --detach --pidfile="./run/celery/%n.pid"
celery -A celery_main worker -Q finance -c 10 -n workerfinance@%h -l INFO --detach  --pidfile="./run/celery/%n.pid"
## On Windows
celery -A celery_main worker --loglevel=INFO -P solo
celery -A celery_main worker -Q corpAZ -P solo -c 10 -n workercorpAZ@%h -l INFO
celery -A celery_main worker -Q finance -P solo -c 10 -n workerfinance@%h -l INFO

# Clear tasks for a celery worker
celery purge -A celery_main -f

# Send tasks to the worker
At the `functions` folder of the project
```
python3
from celery_tasks import *
crawl_task.delay()
```
or
```
python -m celery_run_tasks
```
