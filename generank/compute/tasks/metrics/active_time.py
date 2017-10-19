from datetime import timedelta

from celery import shared_task, chord, group
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone

from generank.compute.contextmanagers import record
from generank.api import models


def get_relevant_score_values(user, day, series):
    """ Return a list of numbers which represent the total active time
    for any sample that occurred on the given day for a given user.
    """
    start_of_day = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    identifier = models.HealthSampleIdentifier.objects.get(
        value=settings.STEP_COUNT_ACTIVITY_IDENTIFIER
    )

    step_counts = models.HealthSample.objects.filter(
        identifier=identifier,
        start_date__gte=start_of_day,
        end_date__lt=end_of_day,
        user=user
    ).only('value')
    for count in step_counts:
        # Returns the step count active time in minutes.
        yield (count.end_date - count.start_date).seconds / 60


def is_new_personal_best(user, value, series):
    """ For a given user and series, check if the new value is that user's
    personal best score for that series. If it is, deactivate the previous
    personal best score.
    """
    try:
        previous_best = models.LifestyleMetricScore.objects.get(
            user=user, series=series, is_personal_best=True
        )
    except ObjectDoesNotExist:
        # The user has no personal best, so the given value can be it.
        return True
    if previous_best.value > value:
        return False

    previous_best.is_personal_best = False
    previous_best.save()
    return True


def recover_personal_best(user, value, series):
    """ Somehow multiple values have been saved as the user's personal best.
    Normally this doesn't happen, but can occur during multiple runs if the
    system reboots and recalculates the user's value.

    This function will recover the most recent personal best score for the given
    series and return if the given value is indeed the correct personal best.
    """
    incorrect_previous_bests = models.LifestyleMetricScore.objects.filter(
        user=user,
        series=series,
        is_personal_best=True
    ).order_by('-created_on')[1:]

    for best in incorrect_previous_bests:
        best.is_personal_best = False
        best.save()

    # Will throw if, for some reason, the recovery didn't work.
    return is_new_personal_best(user, value, series)


def update_scores_for(user, day, series):
    """ Given a user, day and series update the score for that user on
    that day in that series  with the newest sum of the the relevant scores.
    """
    start_of_day = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    try:
        day_active_time = models.LifestyleMetricScore.objects.get(
            series=series,
            user=user,
            created_on__lt=end_of_day,
            created_on__gte=start_of_day
        )
    except ObjectDoesNotExist:
        day_active_time = models.LifestyleMetricScore(
            series=series, user=user, created_on=day)
    scores = get_relevant_score_values(user, day, series)
    day_active_time.value = round(sum(scores), 2)

    try:
        is_personal_best = is_new_personal_best(user, day_active_time.value, series)
    except MultipleObjectsReturned:
        is_personal_best = recover_personal_best(user, day_active_time.value, series)

    if is_personal_best:
        day_active_time.is_personal_best = True
    day_active_time.save()


@shared_task
def update_active_time_status(status_id):
    with record('tasks.metrics.update_active_time_status'):
        status = models.LifestyleMetricStatus.objects.get(id=status_id)
        today = timezone.now()
        yesterday = today - timedelta(days=1)
        for day in [yesterday, today]:
            update_scores_for(status.user, day, status.metric.series.first())
        status.last_updated = timezone.now()
        status.save()
