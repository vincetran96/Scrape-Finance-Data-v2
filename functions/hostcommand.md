# Create directories
localData
localData/PDFs
logs

# Run redis

# Run rabbitmq broker
rabbitmq

# Start a celery worker
celery -A tasks worker --loglevel=INFO

# Send tasks to the worker
At the root folder of the project
```
python3
from tasks import *
crawl_task.delay()
```