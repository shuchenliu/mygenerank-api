import os

from django.conf import settings
from django.utils import timezone

from .base import AuthorizationRequiredAPITestMixin, PublicAPITestMixin, MyGeneRankTestCase

from .. import models


MODULE_PATH = os.path.dirname(os.path.dirname(__file__))
PDF_FIXTURE_PATH = os.path.abspath(os.path.join(MODULE_PATH, 'fixtures', 'consent_forms'))


class UsersAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = '/api/users/'


class UsersRegistrationAPIViewTestCase(PublicAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = None

    def setUp(self):
        super(UsersRegistrationAPIViewTestCase, self).setUp()
        self.RESOURCE_URL = '/api/users/{}/register/'.format(self.test_user.id.hex)


class CreateUsersAPIViewTestCase(PublicAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = '/api/register/'

    # GET

    def test_get(self):
        r = self.client.get(self.RESOURCE_URL)
        self.assertEqual(r.status_code, 405)

    # POST

    def test_post(self):
        data = {
            'username': 'tester@test.com',
            'password': 'tester9456'
        }
        r = self.client.post(self.RESOURCE_URL, data)
        self.assertEqual(r.status_code, 201)

    def test_invalid_post(self):
        data = {
            'username': 'tester@test.com',
        }
        r = self.client.post(self.RESOURCE_URL, data)
        self.assertEqual(r.status_code, 400)

    def test_short_password_post(self):
        data = {
            'username': 'tester@test.com',
            'password': 'te'
        }
        r = self.client.post(self.RESOURCE_URL, data)
        self.assertEqual(r.status_code, 400)

    def test_username_not_email_post(self):
        data = {
            'username': 'tester',
            'password': 'tester9456'
        }
        r = self.client.post(self.RESOURCE_URL, data)
        self.assertEqual(r.status_code, 400)

    def test_username_missing_post(self):
        data = {
            'password': 'tester9456'
        }
        r = self.client.post(self.RESOURCE_URL, data)
        self.assertEqual(r.status_code, 400)


class ConsentFormAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
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


class SignaturesAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
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

