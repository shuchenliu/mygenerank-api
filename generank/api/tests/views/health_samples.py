from django.conf import settings
from django.db import transaction

from .base import AuthorizationRequiredAPITestMixin, MyGeneRankTestCase

from ... import models


class HealthSamplesFeedAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = '/api/health-samples/'

    def setUp(self):
        sample_identifier = models.HealthSampleIdentifier.objects.create(value='HKStepCount')
        models.HealthSampleIdentifier.objects.create(value='HKQuantityTypeIdentifierFlightsClimbed')
        super(HealthSamplesFeedAPIViewTestCase, self).setUp()

    # GET

    def test_authorized_get(self):
        r = self.client.get(self.RESOURCE_URL, **self.auth_headers)
        self.assertEqual(r.status_code, 404)

    def test_authorized_get_with_results(self):
        data = {
            'identifier': 'HKStepCount',
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
            'value': '10',
            'start_date': '2017-09-13 00:32:33.617238+00:00',
            'end_date': '2017-09-13 00:34:33.617238+00:00',
            'units': 'steps'
        }
        r = self.client.post(self.RESOURCE_URL, data, **self.auth_headers)
        self.assertEqual(r.status_code, 201)

    def test_authorized_post2(self):
        data = {
          "identifier": "HKQuantityTypeIdentifierFlightsClimbed",
          "user": "https:\/\/mygenerank.scripps.edu\/api\/users\/80550d42-d499-4052-9911-8f2fd173db9f\/",
          "value": 1,
          "start_date": "2017-09-26T18:47:56",
          "end_date": "2017-09-26T18:47:56",
          "units": "count"
        }
        # Intentionally creating integrity exceptions breaks unit tests.
        # https://stackoverflow.com/a/23326971/2085172
        with transaction.atomic():
            r = self.client.post(self.RESOURCE_URL, data, **self.auth_headers)
            r = self.client.post(self.RESOURCE_URL, data, **self.auth_headers)
        self.assertEqual(r.status_code, 400)
