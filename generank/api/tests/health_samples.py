from django.conf import settings

from .base import BaseAPITestMixin, MyGeneRankTestCase

from .. import models


class HealthSamplesFeedAPIViewTestCase(BaseAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = '/api/health-samples/'

    def setUp(self):
        sample_identifier = models.HealthSampleIdentifier.objects.create(value='HKStepCount')
        super(HealthSamplesFeedAPIViewTestCase, self).setUp()

    # GET

    def test_authorized_get(self):
        r = self.client.get(self.RESOURCE_URL, **self.auth_headers)
        self.assertEqual(r.status_code, 404)

    def test_authorized_get_with_results(self):
        data = {
            'identifier': 'HKStepCount',
            'user': '/api/users/{}/'.format(self.test_user.id),
            'value': '10',
            'start_date': '2017-09-13 00:32:33.617238+00:00',
            'end_date': '2017-09-13 00:34:33.617238+00:00',
            'units': 'steps'
        }
        r = self.client.post(self.RESOURCE_URL, data, **self.auth_headers)
        self.assertEqual(r.status_code, 201)

        r = self.client.get(self.RESOURCE_URL, **self.auth_headers)
        print(r.content)
        self.assertEqual(r.status_code, 200)

    # POST

    def test_invalid_post(self):
        r = self.client.post(self.RESOURCE_URL, **self.auth_headers)
        self.assertEqual(r.status_code, 400)

    def test_authorized_post(self):
        data = {
            'identifier': 'HKStepCount',
            'user': '/api/users/{}/'.format(self.test_user.id),
            'value': '10',
            'start_date': '2017-09-13 00:32:33.617238+00:00',
            'end_date': '2017-09-13 00:34:33.617238+00:00',
            'units': 'steps'
        }
        r = self.client.post(self.RESOURCE_URL, data, **self.auth_headers)
        self.assertEqual(r.status_code, 201)
