from datetime import timedelta
import json, os, uuid
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import TestCase

from generank.api import models, tasks
from generank.twentythreeandme.management.commands import convertfile
from generank.twentythreeandme.models import User, Genotype, Profile

UserModel = get_user_model()

MODULE_PATH = os.path.dirname(__file__)
GENOTYPE_FIXTURE_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(MODULE_PATH))), 'compute', 'fixtures', 'genotypes')
)


class ConvertFileTestCase(TestCase):

    def setUp(self):
        self.condition = models.Condition(name='Test condition')
        self.condition2 = models.Condition(name='Test condition 2')
        self.population = models.Population(name='Test population')

        # Set up activities
        for study_id in settings.DEFAULT_STUDY_IDS:
            models.Activity.objects.create(study_task_identifier=study_id)

        self.test_user = UserModel.objects.create_user(
            "bar_user",
            "dev@example.com"
        )

        profile_id = 'test_api_profile_id'
        self.user = User.objects.create(api_user_id=self.test_user.id, user_id='test')
        self.profile = Profile.objects.create(genotyped=True, user=self.user, profile_id=profile_id)
        self.genotype = Genotype.objects.create(profile=self.profile)

        with open(os.sep.join((GENOTYPE_FIXTURE_PATH, 'test_genotype.vcf'))) as fp:
            self.genotype.genotype_file.save(
                name=uuid.uuid4().hex, content=ContentFile(fp.read())
            )

    @mock.patch('generank.twentythreeandme.tasks._convert_genotype.delay')
    def test_handle(self, delay):
        r = convertfile.Command().handle(
            user_id=self.user.api_user_id,
            profile_id=self.profile.profile_id
        )
        self.assertTrue(delay.called)


    @mock.patch('generank.twentythreeandme.tasks._convert_genotype.delay')
    def test_handle_no_user(self, delay):
        self.user.delete()
        r = convertfile.Command().handle(
            user_id=self.user.api_user_id,
            profile_id=self.profile.profile_id
        )
        self.assertFalse(delay.called)


    @mock.patch('generank.twentythreeandme.tasks._convert_genotype.delay')
    def test_handle_no_profile(self, delay):
        self.profile.delete()
        r = convertfile.Command().handle(
            user_id=self.user.api_user_id,
            profile_id=self.profile.profile_id
        )
        self.assertFalse(delay.called)

    @mock.patch('generank.twentythreeandme.tasks._convert_genotype.delay')
    def test_handle_no_genotype(self, delay):
        self.genotype.delete()
        r = convertfile.Command().handle(
            user_id=self.user.api_user_id,
            profile_id=self.profile.profile_id
        )
        self.assertFalse(delay.called)

    @mock.patch('generank.twentythreeandme.tasks._convert_genotype.delay')
    def test_handle_no_genotype_file(self, delay):
        self.genotype.genotype_file.delete()
        r = convertfile.Command().handle(
            user_id=self.user.api_user_id,
            profile_id=self.profile.profile_id
        )
        self.assertFalse(delay.called)



