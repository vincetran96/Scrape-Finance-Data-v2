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
celery -A celery_main worker --loglevel=INFO
celery -A celery_main worker -Q corpAZ -c 8 -n workercorpAZ@%h -l INFO
celery -A celery_main worker -Q finance -c 8 -n workerfinance@%h -l INFO
## On Windows
celery -A celery_main worker --loglevel=INFO -P solo

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
