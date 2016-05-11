from celery import shared_task

from .models import Genotype, Profile, User
from gene_pc_api.gene_pc_api.models import User as AppUser
from .api_client import *

#import logging

def twentythreeandme_import_task(user_info, token):
    """ Given a token and a user info JSON object this will
    create a API user and  23andMe User and return the API user.
    It will also spawn off processes to create Profile objects and
    import genotype data. """

    ttm_uobj = User.from_json(user_info, token)
    gpc_uobj = AppUser.new_user(ttm_uobj.email)
    ttm_uobj.apiuserid = gpc_uobj.id
    ttm_uobj.save()
    gpc_uobj.save()

    for profile_info in user_info['profiles']:
        twentythreeandme_profile_import_task.delay(ttm_uobj, profile_info,
                                                     token)
    return gpc_uobj


@shared_task
def twentythreeandme_profile_import_task(user, profile_info, token):
    """ Given profile data and a ttm user object this
    function creates objects for profiles associated with
    the given user. """
    profile = Profile.from_json(profile_info, user)
    profile.save()
    twentythreeandme_genotype_import_task.delay(profile,token)

@shared_task
def twentythreeandme_genotype_import_task(profile,token):
    genotype_data = get_genotype_data(token,profile)
    genotype = Genotype.from_json(genotype_data,profile)

@shared_task
def convert_genotype_task(genotype):
    pass

@shared_task
def submit_calculations_task(user_id, profile_id):
    pass
