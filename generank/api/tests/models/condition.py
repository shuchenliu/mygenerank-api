import uuid
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from generank.api import models


UserModel = get_user_model()


class ConditionTestCase(TestCase):

    def setUp(self):
        self.condition = models.Condition(name='Test condition')

    def test_str(self):
        self.assertEqual(self.condition.__str__(), '<API: Condition: Test condition>')


class RiskScoreTestCase(TestCase):

    def setUp(self):
        # Set up activities
        for study_id in settings.DEFAULT_STUDY_IDS:
            models.Activity.objects.create(study_task_identifier=study_id)

        self.test_user = UserModel.objects.create_user("bar_user", "dev@example.com")
        self.condition = models.Condition(name='Test condition')
        self.population = models.Population(name='Test population')

    def test_str(self):
        score = models.RiskScore(
            name='Test score',
            value=0.4,
            user=self.test_user,
            condition=self.condition,
            population=self.population
        )
        self.assertEqual(score.__str__(), '<API: RiskScore: bar_user <API: Condition: Test condition> <API: Population: Test population>>')
