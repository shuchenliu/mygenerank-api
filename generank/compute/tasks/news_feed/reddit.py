""" Fetch and get news feed items from various reddit sources. """

from datetime import timedelta

from celery import shared_task, chord, group
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import praw
from opengraph import OpenGraph

from generank.compute.tasks.util import dmap
from generank.compute.contextmanagers import record
from generank.api import models


SUBREDDITS = (
    ('science', '(flair:health OR flair:biology OR flair:medicine) AND self:no'),
)


def _fetch_from_reddit(client_id, client_secret, username, password):
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent='MyGeneRank Client',
        username=username,
        password=password
    )
    reddit.read_only = True

    for subreddit, query in SUBREDDITS:
        results = reddit.subreddit(subreddit).search(query, syntax='lucene', time_filter='day')
        for submission in results:
            yield submission.url


@shared_task
def _get_urls_from_recent_reddits(client_id, client_secret, username, password, n=1):
    with record('tasks.reddit._get_urls_from_recent_reddits'):
        return [url for url in _fetch_from_reddit(client_id, client_secret, username, password)][0:n]


@shared_task
def _save_opengraph_data_for_url(url):
    with record('tasks.reddit._save_opengraph_data_for_url'):
        if models.Item.objects.filter(link=url).exists():
            return

        og = OpenGraph(url=url)
        item = models.Item(
            title=og.title,
            link=url,
            description=og.description,
            image=getattr(og, 'image', None),
            source=models.Item.SOURCES['reddit']
        )
        item.save()


# Public Methods


@shared_task
def update_news_feed_from_reddit():
    with record('tasks.reddit.update_news_feed_from_reddit'):
        get_urls_from_reddit = _get_urls_from_recent_reddits.si(
            settings.REDDIT_CLIENT_ID,
            settings.REDDIT_CLIENT_SECRET,
            settings.REDDIT_USERNAME,
            settings.REDDIT_PASSWORD
        )

        workflow = (
            get_urls_from_reddit | dmap.s(
                _save_opengraph_data_for_url.s()
            )
        )
        workflow.delay()
