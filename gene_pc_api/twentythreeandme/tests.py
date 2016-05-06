import sure
from .api_client import *
'''
def setup_func():
    print('helloooo')
    settings.configure()
'''

AUTHCODE = ''
TOKEN = get_token(AUTHCODE)

def test_user_import():
    '''
    Given an auth code this should return a User object
    with the user information
    '''
    response = get_user_info(TOKEN)
    response['id'].should.equal("1a91d9493388f6ed")
    response['email'].should.equal("bschrade@scripps.edu")
    response.should.have.key('profiles')
    #response.profiles.should.equal([{"genotyped": True, "id": "SP1_MOTHER_V4"},
    #                        {"genotyped": True, "id": "SP1_FATHER_V4"}])
