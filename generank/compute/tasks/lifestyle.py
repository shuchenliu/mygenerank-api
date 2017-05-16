""" Tasks related to computing the values for a user's Lifestyle Metrics.  """

from celery import shared_task, chord, group
from django.conf import settings

from generank.api import models
from .metrics import active_time


METRIC_TASKS_BY_IDENTIFIER = {
    'ActiveTime': active_time.update_active_time_status,
}


# Dispatch and Expiration Check Tasks


@shared_task
def _find_metric_statuses_to_update():
    """ Return a list of all of the metric status ids that
    need to be updated.
    """
    with record('tasks.lifestyle._find_metric_statuses_to_update'):
        one_day_old = (date.today() - timedelta(days=1))
        expired_statuses = models.LifestyleMetricStatus.objects.filter(
            last_updated__lte=one_day_old
        )
        return [str(status.id) for status in expired_statuses]


@shared_task
def _dispatch_series_value_update(metric_status_id):
    """ Given a user's metric status dispatch the update to another task type
    which will recalculate the metrics.
    """
    with record('tasks.lifestyle._dispatch_series_value_update'):
        status = models.LifestyleMetricStatus.objects.get(id=metric_status_id)
        METRIC_TASKS_BY_IDENTIFIER[status.metric.identifier].delay(metric_status_id)


# Overall Tasks


@shared_task
def dmap(it, callback):
    callback = subtask(callback)
    return group(callback.clone([arg,]) for arg in it)()


@shared_task
def update_user_metrics():
    """ Find all of the user metrics that need to be updated
    and dispatch individual jobs to do so.
    """
    with record('tasks.lifestyle.update_user_metrics'):
        workflow = (
            _find_metric_statuses_to_update.s() | _dmap.s(
                _dispatch_series_value_update.s()
            )
        )
        workflow.delay()
