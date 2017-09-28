import json, os, sure, uuid

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase
import requests
from unittest.mock import MagicMock
from unittest.mock import patch

from .. import api_client, tasks
from ..models import Profile, Genotype, User
from .commands.convertfile import ConvertFileTestCase
import generank.api.models


UserModel = get_user_model()


class mock_response(object):
    def __init__(self,text):
        self.text = text


class TasksTestCase(TestCase):

    def setUp(self):
        self.condition = generank.api.models.Condition(name='Test condition')
        self.condition2 = generank.api.models.Condition(name='Test condition 2')
        self.population = generank.api.models.Population(name='Test population')

        # Set up activities
        for study_id in settings.DEFAULT_STUDY_IDS:
            generank.api.models.Activity.objects.create(study_task_identifier=study_id)

        self.test_user = UserModel.objects.create_user(
            "bar_user",
            "dev@example.com"
        )

        self.profile_id = 'test_api_profile_id'
        self.user = User.objects.create(api_user_id=self.test_user.id, user_id='test')
        self.profile = Profile.objects.create(genotyped=True, user=self.user, profile_id=self.profile_id)
        self.genotype = Genotype.objects.create(profile=self.profile)

    def test_get(self):
        """ Tests the get() function in the api_client. """

        tdata = '{"test":"test123"}'
        requests.get = MagicMock(return_value=mock_response(tdata))
        url = ''
        token = '8c6fdf907e59f829e0da298d3e4a39be'
        response = api_client.get(url,token)

        response['test'].should.equal('test123')

    def test_user_import(self):
        """ Tests the get_user_info() function in the api_client. """

        udata = '{"id": "1a91d9493388f6ed", "profiles": [{"genotyped": true, "id": \
        "SP1_MOTHER_V4"}, {"genotyped": true, "id": "SP1_FATHER_V4"}], "email": \
        "bschrade@scripps.edu"}'
        token = '8c6fdf907e59f829e0da298d3e4a39be'

        requests.get = MagicMock(return_value=mock_response(udata))
        response = api_client.get_user_info(token)

        response['id'].should.equal("1a91d9493388f6ed")
        response['email'].should.equal("bschrade@scripps.edu")
        response.should.have.key('profiles')
        response['profiles'].should.contain({"genotyped": True,
                                                    "id": "SP1_MOTHER_V4"})

    def test_genotype_import(self):
        """ Tests the get_genotype_data() function in the api_client. """

        gdata = '{"id": "SP1_FATHER_V4", "genome": "__AAAAAAAAAAAAAA__AA__GGAA"}'
        token = '8c6fdf907e59f829e0da298d3e4a39be'
        profile = Profile()
        profile.profile_id = 'SP1_FATHER_V4'

        requests.get = MagicMock(return_value=mock_response(gdata))
        response = api_client.get_genotype_data(token,profile)

        response['id'].should.equal("SP1_FATHER_V4")
        response['genome'].should.equal("__AAAAAAAAAAAAAA__AA__GGAA")


    # @patch('generank.twentythreeandme.tasks.get_user_info')
    # def test_twentythreeandme_delayed_import_task(get_user_info):
    #     """ Tests the twentythreeandme_delayed_import_task function from tasks. """
    #
    #     token = '8c6fdf907e59f829e0da298d3e4a39be'
    #     api_userid = uuid.uuid4()
    #     profileid = "SP1_MOTHER_V4"
    #     udata = '{"id": "1a91d9493388f6ed", "profiles": [{"genotyped": true, "id": \
    #     "SP1_MOTHER_V4"}, {"genotyped": true, "id": "SP1_FATHER_V4"}], "email": \
    #     "bschrade@scripps.edu"}'
    #
    #     tasks.get_user_info.return_value = udata
    #     tasks.import_account.delay = MagicMock(return_value = None)
    #
    #     tasks.twentythreeandme_delayed_import_task(token,api_userid,profileid)
    #     tasks.twentythreeandme_import_task.delay.assert_called_with(udata,token,
    #                                                            api_userid,profileid)
    #
    def test_import_account(self):
        """ Tests the twentythreeandme_import_task function from tasks. """

        token = {
            'access_token': '8c6fdf907e59f829e0da298d3e4a39be',
            'expires_in': 3600
        }
        api_userid = uuid.uuid4()
        profileid = uuid.uuid4()

        tasks._import_user.s = MagicMock()
        tasks._import_profile.s = MagicMock()
        tasks._import_genotype.si = MagicMock()

        tasks.import_account(token, api_userid, profileid)

        tasks._import_user.s.called.should.equal(True)
        tasks._import_profile.s.called.should.equal(True)
        tasks._import_genotype.si.called.should.equal(True)


    # @patch('generank.twentythreeandme.tasks.get_genotype_data')
    # def test_twentythreeandme_genotype_import_task(get_genotype_data):
    #     """ Tests the twentythreeandme_genotype_import_task function from tasks. """
    #
    #     gdata = '{"id": "SP1_FATHER_V4", "genome": "__AAAAAAAAAAAAAA__AA__GGAA"}'
    #     get_genotype_data.return_value = json.loads(gdata)
    #     token = '8c6fdf907e59f829e0da298d3e4a39be'
    #
    #     tasks._convert_genotype.delay = MagicMock(return_value=None)
    #     Profile.objects.get = MagicMock(return_value=Profile())
    #
    #     tasks._import_genotype(token, uuid.uuid4(), '')
    #     tasks._convert_genotype.delay.called.should.equal(True)


    @patch('generank.twentythreeandme.tasks.convert')
    def test_convert_genotype_task(self, convert):
        """ Tests the convert_genotype_task function from tasks. """

        gdata = json.loads('{"id": "SP1_FATHER_V4",  \
                                "genome": "__AAAAAAAAAAAAAA__AA__GGAA"}')
        genotype = Genotype.from_json(gdata, Profile.objects.create(genotyped=True))
        genotype.save()
        convert.return_value = 'test'

        tasks._convert_genotype(genotype.id.hex)

        convert.assert_called_with("__AAAAAAAAAAAAAA__AA__GGAA")


    @patch('generank.twentythreeandme.api_client.get_genotype_data')
    def test_import_genotype(self, get_genotype_data):
        """ Tests the 23andMe genotype import. """

        gdata = json.loads('{"id": "SP1_FATHER_V4",  \
                                "genome": "__AAAAAAAAAAAAAA__AA__GGAA"}')
        get_genotype_data.return_value = gdata
        Genotype.from_json = MagicMock(return_value=self.genotype)

        r = tasks._import_genotype('test_token', self.test_user.id, self.profile_id)
        r.should.equal(str(self.genotype.id))
