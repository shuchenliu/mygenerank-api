import sure
from .api_client import *

class temp_response(object):
    def __init__(self,text):
        self.text = text

def mock_gets(data,*args, **kwargs):
    ''' A function to change the behavior of the requests.get fucntion to
    always return the data supplied '''
    resp = temp_response(text=data)
    def temp_f(*args,**kwargs):
        return(resp)
    return temp_f

class mock_function(object):

    def __init__(self,data):
        self.data = data

    def __call__(self,some_function):
        data = self.data
        mock_gets_temp = mock_gets(data=data)
        requests.get = mock_gets_temp

        def wrapper(*args,**kwargs):
            return some_function(*args,**kwargs)

        return wrapper

def test_user_import():
    '''
    Tests the get_user_info() function in the api_client
    '''

    udata = '{"id": "1a91d9493388f6ed", "profiles": [{"genotyped": true, "id": \
    "SP1_MOTHER_V4"}, {"genotyped": true, "id": "SP1_FATHER_V4"}], "email": \
    "bschrade@scripps.edu"}'
    token = '8c6fdf907e59f829e0da298d3e4a39be'

    @mock_function(data=udata)
    def temp(token):
        return get_user_info(token)

    response = temp(token)

    response['id'].should.equal("1a91d9493388f6ed")
    response['email'].should.equal("bschrade@scripps.edu")
    response.should.have.key('profiles')
    #response.profiles.should.equal([{"genotyped": True, "id": "SP1_MOTHER_V4"},
    #                        {"genotyped": True, "id": "SP1_FATHER_V4"}])
