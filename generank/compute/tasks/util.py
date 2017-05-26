from celery import shared_task, group
from django.conf import settings


@shared_task
def dmap(it, callback):
    """ Distributed Map function.
    Given an iterable of tasks and a callback, perform all
    of the tasks and wait before calling the callback.
    """
    callback = subtask(callback)
    return group(callback.clone([arg,]) for arg in it)()


