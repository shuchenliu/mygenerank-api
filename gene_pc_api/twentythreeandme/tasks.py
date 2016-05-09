from celery import shared_task

from .models import Genome, Profile, User
from gene_pc_api.gene_pc_api.models import User as AppUser
from .api_client import get

import logging

def twentythreeandme_import_task(user_info, token):
    """ Given a token and a user info JSON object this will
    create a API user and  23andMe User and return the API user.
    It will also spawn off processes to create Profile objects and
    import genome data"""

    ttm_uobj = User.from_json(user_info, token)
    gpc_uobj = AppUser.new_user(ttm_uobj.email)
    ttm_uobj.apiuserid = gpc_uobj.id
    ttm_uobj.save()
    gpc_uobj.save()

    for profile_info in user_info['profiles']:
        twentythreeandme_profile_import_task.delay(ttm_uobj, profile_info)

    # NOTE - Genome import to be added

    return gpc_uobj

logger = logging.getLogger('celery_task')
@shared_task
def twentythreeandme_profile_import_task(user, profile_info):
    print("Yay I'm alive")
    print(profile_info)

    try:
        pobj = Profile.from_json(profile_info, user)
    except Exception as e:
        print("Yay I'm broken", str(e))

    print("Yay I'm created", pobj)
    pobj.save()
    print("Yay I'm saved")

@shared_task
def submit_calculations_task(user_id, profile_id):
    pass
