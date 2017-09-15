from django.conf import settings

from .base import AuthorizationRequiredAPITestMixin, MyGeneRankTestCase


class LifestyleFeedAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = '/api/lifestyle/'

