# Create directories
localData
localData/PDFs
logs

# Run redis
redis-server

# Run rabbitmq broker
rabbitmq

# Start a celery worker
celery -A celery_main worker --loglevel=INFO
## On Windows
celery -A celery_main worker --loglevel=INFO -P solo

# Clear tasks for a celery worker
celery purge -A celery_main -f

# Send tasks to the worker
At the root folder of the project
```
python3
from celery_tasks import *
crawl_task.delay()
```
