from django.utils import timezone

from generank.api.models import User
from generank.compute.models import TaskStatus


class record():
    """ A simple context manager decorator that records the statuses of tasks. """

    def __init__(self, identifier, user_id=None):
        if user_id is not None:
            user = User.objects.get(id=user_id)
            self.task_status = TaskStatus(identifier=identifier, user=user)
        else:
            self.task_status = TaskStatus(identifier=identifier)

    def __enter__(self):
        self.task_status.start_date = timezone.now()

    def __exit__(self, exc_type, exc_value, traceback):
        self.task_status.end_date = timezone.now()
        succeeded = not exc_type and not exc_value and not traceback
        self.task_status.status = 'Success' if succeeded else 'Fail'
        self.task_status.save()
