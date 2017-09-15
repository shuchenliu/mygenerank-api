from datetime import timedelta
import unittest, uuid
from unittest import mock

from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth import get_user_model
from django.utils import timezone

from generank.api import models
from generank.compute.tasks.lifestyle import active_time


UserModel = get_user_model()


class ActiveTimeTasksTestCase(TestCase):

    def setUp(self):
        # Set up activities
        for study_id in settings.DEFAULT_STUDY_IDS:
            models.Activity.objects.create(study_task_identifier=study_id)

        self.test_user = UserModel.objects.create_user("bar_user", "dev@example.com")

        self.metric = models.LifestyleMetric.objects.create(
            name='Test metric', identifier='test-id'
        )

        self.series = models.LifestyleMetricSeries.objects.create(
            name='Test series', units='some unit'
        )
        self.series.metrics = [self.metric]
        self.series.save()

        self.first_score = models.LifestyleMetricScore.objects.create(
            series=self.series, user=self.test_user, value=10, is_personal_best=False,
            created_on=(timezone.now() - timedelta(days=1))
        )

        self.second_score = models.LifestyleMetricScore.objects.create(
            series=self.series, user=self.test_user, value=15, is_personal_best=True
        )

        self.expired_activity_status = models.LifestyleMetricStatus.objects.create(
            metric=self.metric, last_updated=(timezone.now() - timedelta(hours=6))
        )
        self.active_activity_status = models.LifestyleMetricStatus.objects.create(
            metric=self.metric, last_updated=(timezone.now())
        )

    # Personal Best

    def test_is_not_new_personal_best(self):
        is_best = active_time.is_new_personal_best(self.test_user, 12, self.series)
        self.assertFalse(is_best)

    def test_is_new_personal_best(self):
        is_best = active_time.is_new_personal_best(self.test_user, 18, self.series)
        self.assertTrue(is_best)

    def test_is_new_personal_best_has_no_existing_best(self):
        self.second_score.is_personal_best = False
        self.second_score.save()

        is_best = active_time.is_new_personal_best(self.test_user, 2, self.series)
        self.assertTrue(is_best)

    def test_is_new_personal_best_duplicate_personal_best(self):
        self.first_score.is_personal_best = True
        self.first_score.save()

        is_best = lambda: active_time.is_new_personal_best(self.test_user, 2, self.series)
        self.assertRaises(MultipleObjectsReturned, is_best)

    # Recover Personal Best

    def test_recover_personal_best_fail(self):
        self.first_score.is_personal_best = True
        self.first_score.save()

        is_best = active_time.recover_personal_best(self.test_user, 2, self.series)
        self.assertFalse(is_best)

    def test_recover_personal_best_succeed(self):
        self.first_score.is_personal_best = True
        self.first_score.save()

        is_best = active_time.recover_personal_best(self.test_user, 22, self.series)
        self.assertTrue(is_best)

    # Updating Scores

    def test_update_scores_for_existing(self):
        samples = [12, 2, 31, 4, 35, 63, 2, 5, 7]
        with mock.patch('generank.compute.tasks.metrics.active_time.get_relevant_score_values', return_value=samples):
            day = timezone.now()
            active_time.update_scores_for(self.test_user, day, self.series)

        self.second_score.refresh_from_db()
        self.assertEqual(self.second_score.value, sum(samples))

    def test_update_scores_for_new(self):
        samples = [12, 2, 31, 4, 35, 63, 2, 5, 7]
        with mock.patch('generank.compute.tasks.metrics.active_time.get_relevant_score_values', return_value=samples):
            day = timezone.now() - timedelta(days=3)
            active_time.update_scores_for(self.test_user, day, self.series)

        score = (
            models.LifestyleMetricScore.objects
            .filter(user=self.test_user)
            .order_by('created_on')
        )[0]
        self.assertEqual(score.value, sum(samples))

    def test_update_scores_for_existing_with_duplicates(self):
        self.first_score.is_personal_best = True
        self.first_score.save()

        samples = [12, 2, 31, 4, 35, 63, 2, 5, 7]
        with mock.patch('generank.compute.tasks.metrics.active_time.get_relevant_score_values', return_value=samples):
            day = timezone.now()
            active_time.update_scores_for(self.test_user, day, self.series)

        self.second_score.refresh_from_db()
        self.assertEqual(self.second_score.value, sum(samples))
        self.assertTrue(self.second_score.is_personal_best)

    def test_update_scores_for_new_but_not_best(self):
        samples = [1,]
        with mock.patch('generank.compute.tasks.metrics.active_time.get_relevant_score_values', return_value=samples):
            day = timezone.now() - timedelta(days=3)
            active_time.update_scores_for(self.test_user, day, self.series)

        score = (
            models.LifestyleMetricScore.objects
            .filter(user=self.test_user)
            .order_by('created_on')
        )[0]
        self.assertFalse(score.is_personal_best)
