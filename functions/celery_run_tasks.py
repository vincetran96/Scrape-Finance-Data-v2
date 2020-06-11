# -*- coding: utf-8 -*-
# This module runs task imported from celery_tasks

from celery import group

from celery_tasks import *


if __name__ == '__main__':
    # g = group(multiplier.signature((2,3), immutable=True), subtractor.signature((4,5), immutable=True))
    # adder.apply_async((10,20),link=g)
    # pdfDocs_task.delay()
    

    # g = group(corporateAZ_task.signature(immutable=True),
    #             associates_task.signature(immutable=True),
    #             finance_task.signature(immutable=True))
    # prerun_cleanup_task.apply_async(link=g)
       
    
    # g = group(corporateAZ_task.signature(immutable=True),
    #     associates_task.signature(immutable=True),
    #     finance_task.signature(immutable=True))
    
    # prerun_cleanup_task.apply_async(link=g) 
    
    prerun_cleanup_task.delay()
    corporateAZ_task.delay()
    finance_task.delay()
    associates_task.delay()
    counterparts_task.delay()
    majorshareholders_task.delay()
    ownerstructure_task.delay()
    ctkhdetails_task.delay()
    boarddetails_task.delay()
