import os


from celery import Celery

# set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'twitter.settings')

app = Celery('twitter')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes
# - namespace = 'CELERY' means all celery-related configuration keys
# should have a 'CELERY-' prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# load task modules from all registered Django ap configs
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
