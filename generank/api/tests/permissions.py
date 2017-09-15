import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http.request import HttpRequest
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory, APIClient

from oauth2_provider.models import Application, AccessToken
from oauth2_provider.settings import oauth2_settings

from .. import models, permissions


UserModel = get_user_model()


class PermissionsTestCase(TestCase):

    def setUp(self):
        # Set up activities
        for study_id in settings.DEFAULT_STUDY_IDS:
            models.Activity.objects.create(study_task_identifier=study_id)

        self.test_user = UserModel.objects.create_user("bar_user", "dev@example.com")

        self.request = HttpRequest()
        self.request.user = self.test_user

    def test_has_no_user(self):
        permission = permissions.IsRegistered()
        has = permission.has_permission(HttpRequest(), {})
        self.assertFalse(has)

    def test_has_no_permission(self):
        permission = permissions.IsRegistered()
        has = permission.has_permission(self.request, {})
        self.assertFalse(has)

    def test_has_permission(self):
        self.test_user.registered = True
        permission = permissions.IsRegistered()
        has = permission.has_permission(self.request, {})
        self.assertTrue(has)
