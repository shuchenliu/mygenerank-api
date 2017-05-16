""" A module of risk score calculation tasks.

To add a new score calculation workflow:
- Create a new submodule for the score.
- Import the sumbodule's main method here.
- Add the method to the list of active scores.
"""

from celery import shared_task

from .cad import get_cad_risk_score
from .lifestyle import update_user_metrics


@shared_task
def run_all(user_id, *args, **kwargs):
    """ The base task that runs all other sub-risk score calculation tasks. """
    get_cad_risk_score.s(user_id).delay()
    # TODO: Add more score calculations.
