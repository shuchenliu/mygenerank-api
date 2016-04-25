from celery import shared_task

from .models import Genome, Profile, User
from .api_client import get


@shared_task
def genome_import_task(user_id, profile_id, auth_code):
    pass


@shared_task
def submit_calculations_task(user_id, profile_id):
    pass
