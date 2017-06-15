""" A list of the known bad hosts for domains that could be encountered while
fetching news items from social media sites.

author: Brian Schrader
"""

from generank.api import models


KNOWN_BAD_HOSTS = [
    'www.medscape.com',
]


def is_known_bad_host(url):
    """ Whether the current url is a member of the bad hosts list. """
    return any([True for host in KNOWN_BAD_HOSTS if host in url])


def is_duplicate_of_existing(url, urls=[]):
    """ Using the existing model sets, is this a duplicate of anything in the
    givem list or in the existing data store.
    """
    return (
        any([True for _url in urls if url == _url or url in _url]) or
        models.Item.objects.filter(url__iexact=url).exists()
    )

