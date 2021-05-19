
# This module contains the main Celery app

from celery import Celery


app = Celery('crawlers')
app.config_from_object('celery_config')
