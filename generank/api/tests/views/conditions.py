from unittest import mock

from django.conf import settings

from .base import AuthorizationRequiredAPITestMixin, MyGeneRankTestCase

from ... import models


class ConditionsAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
    """ Tests for the conditions endpoints to prove that they are
    read-only and that all attempts to change the data, authorized or not,
    will fail.
    """
    RESOURCE_URL = '/api/conditions/'


class ConditionsDetailAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
    """ Tests for the conditions endpoints to prove that they are
    read-only and that all attempts to change the data, authorized or not,
    will fail.
    """
    RESOURCE_URL = None

    def setUp(self):
        condition = models.Condition.objects.create(name='Testing Condition')
        self.RESOURCE_URL = '/api/conditions/{}/'.format(condition.id)
        super(ConditionsDetailAPIViewTestCase, self).setUp()


class RiskScoresAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
    """ Tests for the risk-scores endpoints to prove that they are
    read-only and that all attempts to change the data, authorized or not,
    will fail.
    """
    RESOURCE_URL = '/api/risk-scores/'


class RiskScoreDetailAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
    """ Tests for the conditions endpoints to prove that they are
    read-only and that all attempts to change the data, authorized or not,
    will fail.
    """
    RESOURCE_URL = None

    def setUp(self):
        super(RiskScoreDetailAPIViewTestCase, self).setUp()

        condition = models.Condition.objects.create(name='Testing Condition')
        population = models.Population.objects.create(name='Testing Population')
        risk_score = models.RiskScore.objects.create(
            condition=condition, population=population, value=0.10, user=self.test_user)

        self.RESOURCE_URL = '/api/risk-scores/{}/'.format(risk_score.id)


class RiskScorePredictionDetailAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
    """ Tests for the conditions endpoints to prove that they are
    read-only and that all attempts to change the data, authorized or not,
    will fail.
    """
    RESOURCE_URL = None

    def setUp(self):
        super(RiskScorePredictionDetailAPIViewTestCase, self).setUp()

        condition = models.Condition.objects.create(name='Testing Condition')
        population = models.Population.objects.create(name='Testing Population')
        risk_score = models.RiskScore.objects.create(
            condition=condition, population=population, value=0.10, user=self.test_user)
        activity = models.Activity.objects.create(
            study_task_identifier=settings.PHENOTYPE_SURVEY_ID, name='Test Activity')
        answers = {
            settings.SEX_QUESTION_IDENTIFIER: 'male',
            settings.RACIAL_QUESTION_IDENTIFIER: 'white',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 170,
            settings.AGE_QUESTION_IDENTIFIER: 53,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
            settings.PRECISE_TOTAL_CHOLESTEROL_IDENTIFIER: 200,
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
            settings.PRECISE_HDL_CHOLESTEROL_IDENTIFIER: 80,
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: '',
            settings.SYSTOLIC_BLOOD_PRESSURE_IDENTIFIER: 120,
            settings.DIABETES_IDENTIFIER: False,
            settings.SMOKING_IDENTIFIER: False,
            settings.ACTIVITY_IDENTIFIER: True,
            settings.DIET_IDENTIFIER: True,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
        }
        for key, value in answers.items():
            models.ActivityAnswer.objects.create(
                activity=activity, question_identifier=key, value=value, user=self.test_user)

        self.RESOURCE_URL = '/api/risk-scores/{}/predict/'.format(risk_score.id)

    def test_authorized_get(self):
        params = {
            'healthy_weight': 0,
            'healthy_diet': 0,
            'physically_active': 0,
            'non_smoking': 0
        }

        r = self.client.get(self.RESOURCE_URL, params, **self.auth_headers)
        self.assertEqual(r.status_code, 200)

    def test_invalid_get(self):
        r = self.client.get(self.RESOURCE_URL, **self.auth_headers)
        self.assertEqual(r.status_code, 400)


class PopulationsAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
    """ Tests for the poulations endpoints to prove that they are
    read-only and that all attempts to change the data, authorized or not,
    will fail.
    """
    RESOURCE_URL = '/api/populations/'


class PopulationDetailAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
    """ Tests for the conditions endpoints to prove that they are
    read-only and that all attempts to change the data, authorized or not,
    will fail.
    """
    RESOURCE_URL = None

    def setUp(self):
        super(PopulationDetailAPIViewTestCase, self).setUp()

        population = models.Population.objects.create(name='Testing Population')

        self.RESOURCE_URL = '/api/populations/{}/'.format(population.id)



