from celery import shared_task, group, subtask
from django.conf import settings


@shared_task
def dmap(it, callback):
    """ Distributed Map function.
    Given an iterable of data and a task method, map the method over the
    given data.
    """
    callback = subtask(callback)
    return group(callback.clone([arg,]) for arg in it)()


