from django.conf import settings

from .base import AuthorizationRequiredAPITestMixin, MyGeneRankTestCase

from ... import models


class ActivitiesAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = '/api/activities/'


# class ActivityStatusesAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
#     RESOURCE_URL = '/api/activity-statuses/'


class ActivityAnswersAPIViewTestCase(AuthorizationRequiredAPITestMixin, MyGeneRankTestCase):
    RESOURCE_URL = '/api/activity-answers/'


    def setUp(self):
        super(ActivityAnswersAPIViewTestCase, self).setUp()

        self.activity = models.Activity.objects.create(
            study_task_identifier=settings.PHENOTYPE_SURVEY_ID, name='Test Activity')

    def test_authorized_post(self):
        data = {
            'question_identifier': 'TEST ID',
            'value': 'test-data',
            'activity': '/api/activities/{}/'.format(self.activity.id),
        }
        r = self.client.post(self.RESOURCE_URL, data, **self.auth_headers)
        self.assertEqual(r.status_code, 201)
