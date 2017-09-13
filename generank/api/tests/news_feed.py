from django.conf import settings

from .base import BaseAPITestMixin, MyGeneRankTestCase


class NewsFeedAPIViewTestCase(BaseAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = '/api/newsfeed/'

