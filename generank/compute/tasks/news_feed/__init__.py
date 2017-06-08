""" A module that manages fetching new newsfeed items from various sources.

author: Brian Schrader
since: 2017-206-06
"""

from celery import shared_task

from .reddit import update_news_feed_from_reddit


@shared_task
def update_news_feed(*args, **kwargs):
    """ The base task that runs all other subtasks. """
    update_news_feed_from_reddit.s().delay()
