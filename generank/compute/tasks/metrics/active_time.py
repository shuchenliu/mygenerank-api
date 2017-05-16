from datetime import datetime

from celery import shared_task, chord, group
from django.conf import settings

from generank.api import models


def get_relevant_score_values(user, day, series):
    """ Return a list of numbers which represent the total active time
    for any sample that occurred on the given day for a given user.
    """
    pass


def update_scores_for(user, day, series):
    """ Given a user, day and series update the score for that user on
    that day in that series  with the newest sum of the the relevant scores.
    """
    day_active_time = models.LifestyleMetricScore.objects.get(
        series=series, user=status.user, created_on=day)
    day_active_time.value = sum(get_relevant_score_values(user, day, series))
    day_active_time.save()


@shared_task
def update_active_time_status(status_id):
    status = models.LifestyleMetricStatus.objects.filter(id=status_id)
    yesterday = date.today() - timedelta(days=1)
    today = date.today()
    for day in [yesterday, today]:
        update_scores_for(status.user, day, status.metric.series[0])
    status.last_updated = datetime.now()
    status.save()

