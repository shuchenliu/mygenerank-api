import requests
from celery import shared_task

from .models  import User, Profile, Genotype
from .api_client import get_user_info, get_genotype_data


@shared_task
def twentythreeandme_delayed_import_task(token, api_userid, profileid):
    """ Given a token and a api_user and a 23andMe profile_id,
    it fetches user data for that profile from 23andMe and starts
    the task to create a 23andMe User/Profile. """

    try:
        user_info = get_user_info(token)
        # Create a ttm user
        twentythreeandme_import_task.delay(user_info, token, api_userid, profileid)

    except requests.exceptions.Timeout:
        twentythreeandme_delayed_import_task.delay(token, api_userid,
                                                    profileid, countdown = 2)


@shared_task
def twentythreeandme_import_task(user_info, token, api_userid, profileid):
    """ Given a token and a user info JSON object this will
    create a API user and  23andMe User and return the API user.
    It will also spawn off processes to create Profile objects and
    import genotype data. """

    # Create a ttm user
    ttm_uobj = User.from_json(user_info, token)
    ttm_uobj.apiuserid = api_userid
    ttm_uobj.save()

    # Create a profile object
    for prof in user_info['profiles']:
        if prof['id'] == profileid:
            profile = Profile.from_json(prof, ttm_uobj)
            profile.save()
            twentythreeandme_genotype_import_task.delay(profile,token)


@shared_task
def twentythreeandme_genotype_import_task(profile,token):
    try:
        genotype_data = get_genotype_data(token,profile)
        genotype = Genotype.from_json(genotype_data,profile)
        genotype.save()
    except requests.exceptions.Timeout:
        twentythreeandme_genotype_import_task.delay(profile,token, countdown=2)


@shared_task
def convert_genotype_task(genotype):
    pass


@shared_task
def submit_calculations_task(user_id, profile_id):
    pass
