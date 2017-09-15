from django.conf import settings

from .base import AuthorizationRequiredAPITestMixin, MyGeneRankTestCase


class NewsFeedAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = '/api/newsfeed/'

