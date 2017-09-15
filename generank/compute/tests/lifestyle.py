from datetime import timedelta
import unittest, uuid
from unittest import mock

from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.utils import timezone

from generank.api import models
from ..tasks import lifestyle


UserModel = get_user_model()


class LifestyleTasksTestCase(TestCase):

    def setUp(self):
        # Set up activities
        for study_id in settings.DEFAULT_STUDY_IDS:
            models.Activity.objects.create(study_task_identifier=study_id)

        self.test_user = UserModel.objects.create_user("bar_user", "dev@example.com")

        self.metric = models.LifestyleMetric.objects.create(
            name='Test Series', identifier='test-id'
        )
        self.expired_activity_status = models.LifestyleMetricStatus.objects.create(
            metric=self.metric, last_updated=(timezone.now() - timedelta(hours=6))
        )
        self.active_activity_status = models.LifestyleMetricStatus.objects.create(
            metric=self.metric, last_updated=(timezone.now())
        )


    def test_find_metric_statuses_to_update(self):
        ids = lifestyle._find_metric_statuses_to_update()
        self.assertEqual(ids[0], str(self.expired_activity_status.id))


