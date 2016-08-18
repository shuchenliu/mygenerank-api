from unittest.mock import MagicMock
from unittest.mock import patch

import sure
import json

from . import api_client
from .models import Profile, Genotype
from .tasks import *
from generank.api.models import User as ApiUser

class mock_response(object):
    def __init__(self,text):
        self.text = text

def test_get():
    """ Tests the get() function in the api_client. """

    tdata = '{"test":"test123"}'
    requests.get = MagicMock(return_value=mock_response(tdata))
    url = ''
    token = '8c6fdf907e59f829e0da298d3e4a39be'
    response = api_client.get(url,token)

    response['test'].should.equal('test123')

def test_user_import():
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

def test_genotype_import():
    """ Tests the get_genotype_data() function in the api_client. """

    gdata = '{"id": "SP1_FATHER_V4", "genome": "__AAAAAAAAAAAAAA__AA__GGAA"}'
    token = '8c6fdf907e59f829e0da298d3e4a39be'
    profile = Profile()
    profile.profile_id = 'SP1_FATHER_V4'

    requests.get = MagicMock(return_value=mock_response(gdata))
    response = api_client.get_genotype_data(token,profile)

    response['id'].should.equal("SP1_FATHER_V4")
    response['genome'].should.equal("__AAAAAAAAAAAAAA__AA__GGAA")

@patch('generank.twentythreeandme.tasks.get_user_info')
def test_twentythreeandme_delayed_import_task(get_user_info):
    """ Tests the twentythreeandme_delayed_import_task function from tasks. """

    token = '8c6fdf907e59f829e0da298d3e4a39be'
    api_userid = ApiUser().id
    profileid = "SP1_MOTHER_V4"
    udata = '{"id": "1a91d9493388f6ed", "profiles": [{"genotyped": true, "id": \
    "SP1_MOTHER_V4"}, {"genotyped": true, "id": "SP1_FATHER_V4"}], "email": \
    "bschrade@scripps.edu"}'

    get_user_info.return_value = udata
    twentythreeandme_import_task.delay = MagicMock(return_value = None)

    twentythreeandme_delayed_import_task(token,api_userid,profileid)
    twentythreeandme_import_task.delay.assert_called_with(udata,token,
                                                           api_userid,profileid)

def test_twentythreeandme_import_task():
    """ Tests the twentythreeandme_import_task function from tasks. """

    token = '8c6fdf907e59f829e0da298d3e4a39be'
    api_userid = ApiUser().id
    profileid = "SP1_MOTHER_V4"
    udata = json.loads('{"id": "1a91d9493388f6ed", "profiles": [{"genotyped": \
    true, "id": "SP1_MOTHER_V4"}, {"genotyped": true, "id": "SP1_FATHER_V4"}], \
    "email": "bschrade@scripps.edu"}')

    twentythreeandme_genotype_import_task.delay = MagicMock(return_value = None)
    twentythreeandme_import_task(udata,token,api_userid,profileid)
    twentythreeandme_genotype_import_task.delay.called.should.equal(True)

@patch('generank.twentythreeandme.tasks.get_genotype_data')
def test_twentythreeandme_genotype_import_task(get_genotype_data):
    """ Tests the twentythreeandme_genotype_import_task function from tasks. """

    gdata = '{"id": "SP1_FATHER_V4", "genome": "__AAAAAAAAAAAAAA__AA__GGAA"}'
    get_genotype_data.return_value = json.loads(gdata)
    token = '8c6fdf907e59f829e0da298d3e4a39be'

    convert_genotype_task.delay = MagicMock(return_value=None)

    twentythreeandme_genotype_import_task(Profile(),token)
    convert_genotype_task.delay.called.should.equal(True)

@patch('generank.twentythreeandme.tasks.convert')
def test_convert_genotype_task(convert):
    """ Tests the convert_genotype_task function from tasks. """

    gdata = json.loads('{"id": "SP1_FATHER_V4",  \
                            "genome": "__AAAAAAAAAAAAAA__AA__GGAA"}')
    genotype = Genotype.from_json(gdata,Profile())
    convert.return_value = 'test'

    convert_genotype_task(genotype)
    convert.assert_called_with("__AAAAAAAAAAAAAA__AA__GGAA")
