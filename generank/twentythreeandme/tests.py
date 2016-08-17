import sure
from .api_client import *
from .models import Profile

class mock_response(object):
    def __init__(self,text):
        self.text = text

def mock_gets(data,*args, **kwargs):
    ''' A function to change the behavior of the requests.get fucntion to
    always return the data supplied '''
    resp = mock_response(text=data)
    def temp_f(*args,**kwargs):
        return(resp)
    return temp_f

class mock_function(object):
    ''' A decorator which helps in mocking a function such that the
    requests.get call returns the data supplied. '''
    def __init__(self,data):
        self.data = data

    def __call__(self,some_function):
        data = self.data
        requests.get = mock_gets(data=data)

        def wrapper(*args,**kwargs):
            return some_function(*args,**kwargs)

        return wrapper

def test_user_import():
    ''' Tests the get_user_info() function in the api_client. '''

    udata = '{"id": "1a91d9493388f6ed", "profiles": [{"genotyped": true, "id": \
    "SP1_MOTHER_V4"}, {"genotyped": true, "id": "SP1_FATHER_V4"}], "email": \
    "bschrade@scripps.edu"}'
    token = '8c6fdf907e59f829e0da298d3e4a39be'

    @mock_function(data=udata)
    def mocked_get_user_info(token):
        return get_user_info(token)

    response = mocked_get_user_info(token)

    response['id'].should.equal("1a91d9493388f6ed")
    response['email'].should.equal("bschrade@scripps.edu")
    response.should.have.key('profiles')
    response['profiles'].should.contain({"genotyped": True, "id": "SP1_MOTHER_V4"})


def test_genotype_import():
    ''' Tests the get_genotype_data() function in the api_client. '''

    gdata = '{"id": "SP1_FATHER_V4", "genome": "__AAAAAAAAAAAAAA__AA__GGAA"}'
    token = '8c6fdf907e59f829e0da298d3e4a39be'
    profile = Profile()
    profile.profile_id = 'SP1_FATHER_V4'

    @mock_function(data=gdata)
    def mocked_get_user_info(token,profile):
        return get_genotype_data(token,profile)

    response = mocked_get_user_info(token,profile)

    response['id'].should.equal("SP1_FATHER_V4")
    response['genome'].should.equal("__AAAAAAAAAAAAAA__AA__GGAA")
