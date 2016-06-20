from django.conf import settings
from . import celery

celery  # bootstrap Celery

settings.configure()
