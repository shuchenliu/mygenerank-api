import os

from django.conf import settings
from django.utils import timezone

from .base import BaseAPITestMixin, MyGeneRankTestCase

from .. import models


MODULE_PATH = os.path.dirname(os.path.dirname(__file__))
PDF_FIXTURE_PATH = os.path.abspath(os.path.join(MODULE_PATH, 'fixtures', 'consent_forms'))


class UsersAPIViewTestCase(BaseAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = '/api/users/'


class ConsentFormAPIViewTestCase(BaseAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = '/api/consent-forms/'

    def test_authorized_post(self):
        with open(os.sep.join((PDF_FIXTURE_PATH, 'sample_consent.pdf')), 'rb') as f:
            data = {
                'user': '/api/users/{}/'.format(self.test_user.id.hex),
                'consent_pdf': f,
                'name': 'sample_consent.pdf'
            }
            r = self.client.post(self.RESOURCE_URL, data, **self.auth_headers)
        print(r.content)
        self.assertEqual(r.status_code, 201)


class SignaturesAPIViewTestCase(BaseAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = '/api/signatures/'

    def setUp(self):
        super(SignaturesAPIViewTestCase, self).setUp()

        self.consent_form = models.ConsentPDF.objects.create(user=self.test_user)

    def test_authorized_post(self):
        data = {
            'date_signed': timezone.now().strftime('%Y-%m-%d'),
            'consent_pdf': '/api/consent-forms/{}/'.format(self.consent_form.id.hex)
        }
        r = self.client.post(self.RESOURCE_URL, data, **self.auth_headers)
        self.assertEqual(r.status_code, 201)

