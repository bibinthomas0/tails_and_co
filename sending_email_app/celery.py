from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_with_celery.settings')

app = Celery('django_with_celery')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'expire-records-daily': {
        'task': 'owner.tasks.expire_records',
        'schedule': crontab(minute=0, hour=0),  
    },
    'expire-coupons-daily': {
        'task': 'owner.tasks.expire_coupons',
        'schedule': crontab(minute=0, hour=0), 
    },
    'expire-returnpolicy-daily': {
        'task': 'owner.tasks.expire_returnpolicy',
        'schedule': crontab(minute=0, hour=0),  
    },
}

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
    
# Set the new configuration for broker connection retries
app.conf.broker_connection_retry = True
app.conf.broker_connection_retry_on_startup = True
