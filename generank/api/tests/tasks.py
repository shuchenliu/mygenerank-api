from datetime import timedelta
import uuid
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from generank.api import models, tasks


UserModel = get_user_model()


class TasksTestCase(TestCase):

    def setUp(self):
        self.condition = models.Condition(name='Test condition')
        self.condition2 = models.Condition(name='Test condition 2')
        self.population = models.Population(name='Test population')

        # Set up activities
        for study_id in settings.DEFAULT_STUDY_IDS:
            models.Activity.objects.create(study_task_identifier=study_id)

        self.followup_activity = models.Activity.objects.create(
            study_task_identifier=settings.POST_CAD_6MO_SURVEY_ID
        )

        self.post_results_activity = models.Activity.objects.create(
            study_task_identifier=settings.POST_CAD_RESULTS_SURVEY_ID
        )

        # Expired
        self.test_user = UserModel.objects.create_user(
            "bar_user",
            "dev@example.com"
        )

        models.RiskScore.objects.create(value=0.3,
            user=self.test_user,
            condition=self.condition,
            population=self.population,
            created_on=(timezone.now() - timedelta(weeks=25))
        )

        # Not-expired
        self.test_user2 = UserModel.objects.create_user(
            "bar_user2",
            "dev2@example.com"
        )

        models.RiskScore.objects.create(value=0.3,
            user=self.test_user2,
            condition=self.condition,
            population=self.population,
            created_on=(timezone.now() - timedelta(weeks=10))
        )

        # Delete the auto-created statuses so we can test them.
        queryset = models.ActivityStatus.objects.filter(
            user=self.test_user, activity=self.post_results_activity
        ).delete()


    def test_send_followup_survey_to_users(self):
        queryset = models.ActivityStatus.objects.filter(
            user=self.test_user, activity=self.followup_activity
        )
        self.assertFalse(queryset.exists())

        tasks.send_followup_survey_to_users()

        queryset = models.ActivityStatus.objects.filter(
            user=self.test_user, activity=self.followup_activity
        )
        self.assertTrue(queryset.exists())

    def test_send_post_cad_survey_to_users(self):
        queryset = models.ActivityStatus.objects.filter(
            user=self.test_user, activity=self.post_results_activity
        )
        self.assertFalse(queryset.exists())

        tasks.send_post_cad_survey_to_users(self.test_user.id.hex)

        queryset = models.ActivityStatus.objects.filter(
            user=self.test_user, activity=self.post_results_activity
        )
        self.assertTrue(queryset.exists())

    def test_send_post_cad_survey_to_users_expired(self):
        self.test_user.is_active = False
        self.test_user.save()

        queryset = models.ActivityStatus.objects.filter(
            user=self.test_user, activity=self.post_results_activity
        )
        self.assertFalse(queryset.exists())

        tasks.send_post_cad_survey_to_users(self.test_user.id.hex)

        queryset = models.ActivityStatus.objects.filter(
            user=self.test_user, activity=self.post_results_activity
        )
        self.assertFalse(queryset.exists())
