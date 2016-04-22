""" Client functions for the 23andMe API. """

import json

import requests


def get(url, profile_id, auth_code, model):
    """ Given a resource URL, profile_id and auth_code, return
    the response from the API mapped to the given model.
    Note: model must adhere to the `from_json` interface.
    """
    headers = {
        'Authorization' : 'Bearer: {auth_code}'.format(auth_code=auth_code)
        }
    response = requests.get(url, headers=headers)
    return model.from_json(json.loads(response.text))
