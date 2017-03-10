""" A module for calculating leaderboards. """
from datetime import datetime, timedelta

from celery import shared_task, chord, group
from celery.utils.log import get_task_logger

from generank.api import models


@shared_task
def get_leaderboard_status(user_id):
    """ For a given user extract the summary of their activity for a given
    week and rank it against the others in their risk category.
    """
    with record('tasks.leaderboard.get_leaderboard_status', user_id):
        walking_activity = models.HealthSample.objects.filter(
            user__id=user_id,
            start_date__gte=datetime.utcnow() - timedelta(days=7),
            identifier="HKWalkRun"
        )
        total_step_count = sum([sample.value for sample in walking_activity])
        rank = len(ActivityScore.objects.filter(
            value__gt=total_step_count,
            created_on__gte=datetime.utcnow() - timedelta(days=7),
        ))

        previous = ActivityScore.objects.all().order_by('-created_on')[0]
        delta = previous.rank - rank

        return total_step_count, rank, delta


@shared_task
def store_results(user_id, value, rank, delta)
    with record('tasks.leaderboard.store_results', user_id):
        user = User.objects.get(id=user_id)
        score = models.ActivityScore(user=user, value=value, rank=rank, delta=delta)
        score.save()
