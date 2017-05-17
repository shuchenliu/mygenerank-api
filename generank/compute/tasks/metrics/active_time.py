from datetime import timedelta

from celery import shared_task, chord, group
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from generank.api import models


def get_relevant_score_values(user, day, series):
    """ Return a list of numbers which represent the total active time
    for any sample that occurred on the given day for a given user.
    """
    start_of_day = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    identifier = models.HealthSampleIdentifier.objects.get(
        value=settings.STEP_COUNT_ACTIVITY_IDENTIFIER)

    step_counts = models.HealthSample.objects.filter(
        identifier=identifier, start_date__gte=start_of_day,
        end_date__lt=end_of_day).only('value')
    for count in step_counts:
        yield count.value


def update_scores_for(user, day, series):
    """ Given a user, day and series update the score for that user on
    that day in that series  with the newest sum of the the relevant scores.
    """
    start_of_day = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    try:
        day_active_time = models.LifestyleMetricScore.objects.get(
            series=series, user=user, created_on__lt=end_of_day,
            created_on__gte=start_of_day)
    except ObjectDoesNotExist:
        day_active_time = models.LifestyleMetricScore(
            series=series, user=user, created_on=day)
    day_active_time.value = sum(get_relevant_score_values(user, day, series))
    day_active_time.save()


@shared_task
def update_active_time_status(status_id):
    status = models.LifestyleMetricStatus.objects.get(id=status_id)
    today = timezone.now()
    yesterday = today - timedelta(days=1)
    for day in [yesterday, today]:
        update_scores_for(status.user, day, status.metric.series.first())
    status.last_updated = timezone.now()
    status.save()

