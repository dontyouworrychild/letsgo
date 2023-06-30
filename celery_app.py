import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letsgo.settings')

app = Celery('letsgo')
app.config_from_object('django.conf:settings')
app.conf.broker_url = settings.CELERY_BROKER_URL

app.autodiscover_tasks()