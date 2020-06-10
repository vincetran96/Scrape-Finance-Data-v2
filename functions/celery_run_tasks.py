# -*- coding: utf-8 -*-
# This module runs task imported from celery_tasks

from celery import group

from celery_tasks import *


if __name__ == '__main__':
    # g = group(multiplier.signature((2,3), immutable=True), subtractor.signature((4,5), immutable=True))
    # adder.apply_async((10,20),link=g)
    # pdfDocs_task.delay()
    corporateAZ_task.delay()
    # finance_task.delay()
    # associates_task()
    counterparts_task()
    
