from django.conf import settings

from .base import BaseAPITestMixin, MyGeneRankTestCase


class LifestyleFeedAPIViewTestCase(BaseAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = '/api/lifestyle/'

