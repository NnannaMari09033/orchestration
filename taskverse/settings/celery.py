# from taskverse.env import env

# CELERY_BROKER = env('CELERY_BROKER')

# CELERY_RESULT_BACKEND='django_db'
# CELERY_RESULT_EXTENDED=True

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskverse.django.base')

app = Celery('taskverse')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')