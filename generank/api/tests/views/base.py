import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory, APIClient

from oauth2_provider.models import Application, AccessToken
from oauth2_provider.settings import oauth2_settings

from ... import models


UserModel = get_user_model()


class MyGeneRankTestCase(TestCase):

    def setUp(self):
        # Set up activities
        for study_id in settings.DEFAULT_STUDY_IDS:
            models.Activity.objects.create(study_task_identifier=study_id)

        self.test_user = UserModel.objects.create_user("bar_user", "dev@example.com")

        self.application = Application(
            name="Test Application",
            redirect_uris="http://localhost http://example.com http://example.org",
            user=self.test_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.application.save()

        self.valid_token = AccessToken.objects.create(
            user=self.test_user, token="12345678901",
            application=self.application,
            expires=timezone.now() + datetime.timedelta(days=1),
            scope="read write"
        )

        oauth2_settings._SCOPES = ["read", "write", "introspection", "dolphin"]
        oauth2_settings.READ_SCOPE = "read"
        oauth2_settings.WRITE_SCOPE = "write"

    def tearDown(self):
        oauth2_settings._SCOPES = ["read", "write"]
        AccessToken.objects.all().delete()
        Application.objects.all().delete()
        UserModel.objects.all().delete()
        models.Activity.objects.all().delete()


class PublicAPITestMixin(object):
    RESOURCE_URL = None

    # GET

    def test_get(self):
        r = self.client.get(self.RESOURCE_URL)
        self.assertEqual(r.status_code, 200)

    # POST

    def test_post(self):
        r = self.client.post(self.RESOURCE_URL)
        self.assertEqual(r.status_code, 405)

    # PUT

    def test_put(self):
        r = self.client.put(self.RESOURCE_URL)
        self.assertEqual(r.status_code, 405)

    # PATCH

    def test_patch(self):
        r = self.client.patch(self.RESOURCE_URL)
        self.assertEqual(r.status_code, 405)

    # DELETE

    def test_delete(self):
        r = self.client.delete(self.RESOURCE_URL)
        self.assertEqual(r.status_code, 405)


class AuthorizationRequiredAPITestMixin(object):
    RESOURCE_URL = None

    @property
    def auth_headers(self):
        return {
            "HTTP_AUTHORIZATION": "Bearer " + self.valid_token.token,
        }

    @property
    def invalid_auth_headers(self):
        return {
            "HTTP_AUTHORIZATION": "Bearer " + 'fake_token',
        }

    # GET

    def test_authorized_get(self):
        r = self.client.get(self.RESOURCE_URL, **self.auth_headers)
        self.assertEqual(r.status_code, 200)

    def test_unauthorized_get(self):
        r = self.client.get(self.RESOURCE_URL, **self.invalid_auth_headers)
        self.assertEqual(r.status_code, 401)

    # POST

    def test_authorized_post(self):
        r = self.client.post(self.RESOURCE_URL, **self.auth_headers)
        self.assertEqual(r.status_code, 405)

    def test_unauthorized_post(self):
        r = self.client.post(self.RESOURCE_URL, **self.invalid_auth_headers)
        self.assertEqual(r.status_code, 401)

    # PUT

    def test_authorized_put(self):
        r = self.client.put(self.RESOURCE_URL, **self.auth_headers)
        self.assertEqual(r.status_code, 405)

    def test_unauthorized_put(self):
        r = self.client.put(self.RESOURCE_URL, **self.invalid_auth_headers)
        self.assertEqual(r.status_code, 401)

    # PATCH

    def test_authorized_patch(self):
        r = self.client.patch(self.RESOURCE_URL, **self.auth_headers)
        self.assertEqual(r.status_code, 405)

    def test_unauthorized_patch(self):
        r = self.client.patch(self.RESOURCE_URL, **self.invalid_auth_headers)
        self.assertEqual(r.status_code, 401)

    # DELETE

    def test_authorized_delete(self):
        r = self.client.delete(self.RESOURCE_URL, **self.auth_headers)
        self.assertEqual(r.status_code, 405)

    def test_unauthorized_delete(self):
        r = self.client.delete(self.RESOURCE_URL, **self.invalid_auth_headers)
        self.assertEqual(r.status_code, 401)

