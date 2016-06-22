from celery import shared_task

from .models  import User, Profile, Genotype
from .api_client import get_user_info, get_genotype_data
import requests
from  django.core.exceptions import ObjectDoesNotExist

@shared_task
def twentythreeandme_delayed_import_task(token, userid):
    """ Given a token and a user info JSON object this will
    create a API user and  23andMe User and return the API user.
    It will also spawn off processes to create Profile objects and
    import genotype data. """

    try:
        user_info = get_user_info(token)
        user_id = user_info['id']
        try:
            """ If a user_id exists already then just display that user """
            existing_user_ttm = User.objects.get(user_id__exact=user_id)

        except ObjectDoesNotExist:
            """ Create a new user and start the import tasks
            if the user doesn't exist """
            twentythreeandme_import_task.delay(user_info, token, userid)

    except requests.exceptions.Timeout:
        twentythreeandme_delayed_import_task.delay(token,userid, countdown = 2)

@shared_task
def twentythreeandme_import_task(user_info, token, userid):
    """ Given a token and a user info JSON object this will
    create a API user and  23andMe User and return the API user.
    It will also spawn off processes to create Profile objects and
    import genotype data. """

    ttm_uobj = User.from_json(user_info, token)
    ttm_uobj.apiuserid = userid
    ttm_uobj.save()

    for profile_info in user_info['profiles']:
        twentythreeandme_profile_import_task.delay(ttm_uobj, profile_info,
                                                             token)

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
