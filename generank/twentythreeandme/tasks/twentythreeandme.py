import os, requests, sys

from celery import shared_task, chord, group
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.utils import IntegrityError

from ..models  import User, Profile, Genotype
from ..api_client import get_user_info, get_genotype_data

sys.path.append(os.environ['PIPELINE_DIRECTORY'].strip())
from conversion.convert_ttm_to_vcf import convert


logger = get_task_logger(__name__)


@shared_task
def twentythreeandme_delayed_import_task(token, api_userid, profileid):
    """ Given a token and a api_user and a 23andMe profile_id,
    it fetches user data for that profile from 23andMe and starts
    the task to create a 23andMe User/Profile.
    """
    logger.debug('tasks.twentythreeandme_delayed_import_task')

    try:
        user_info = get_user_info(token)
    except requests.exceptions.Timeout:
        logger.warning('An timeout occurred, retrying.')
        twentythreeandme_delayed_import_task.delay(token, api_userid,
            profileid, countdown=2)
        return

    twentythreeandme_import_task.delay(user_info, token, api_userid, profileid)


@shared_task
def twentythreeandme_import_task(user_info, token, api_userid, profileid):
    """ Given a token and a user info JSON object this will create a 23andMe
    User. It will also create a Profile object and spawn a job to import the
    genotype data.
    """
    logger.debug('tasks.twentythreeandme_import_task')

    # Create a ttm user
    ttm_uobj = User.from_json(user_info, token)
    ttm_uobj.user_id = api_userid

    try:
        ttm_uobj.save()
    except IntegrityError:
        logger.error('A user with this id already exists.')
        return

    try:
        prof = [prof for prof in user_info['profiles']
            if prof['id'] == profileid][0]
    except IndexError:
        logger.error('No retrieved profile matches {}'.format(profileid))
        return

    # Create a profile object
    profile = Profile.from_json(prof, ttm_uobj)
    profile.save()
    twentythreeandme_genotype_import_task.delay(profile.id, token)


@shared_task
def twentythreeandme_genotype_import_task(profile_id, token):
    """ Given a profile object and a bearer token, this function will download
    the raw genotype data from 23andme and save it in a genotype object and
    spawns a job to convert the raw file into the VCF format.
    """
    logger.debug('tasks.twentythreeandme_genotype_import_task')

    profile = Profile.objects.get(id=profile_id)

    try:
        genotype_data = get_genotype_data(token, profile)
    except requests.exceptions.Timeout:
        logger.warning('An timeout occurred, retrying.')
        twentythreeandme_genotype_import_task.delay(profile,token, countdown=2)

    genotype = Genotype.from_json(genotype_data, profile)

    try:
        genotype.save()
    except IntegrityError:
        logger.error('A genotype for this user already exists.')
        return

    convert_genotype_task.delay(genotype.id)


@shared_task
def convert_genotype_task(genotype_id):
    """ Given a genotype, this function converts the genotype data file from the
    23 and Me format to a VCF format.
    """
    logger.debug('tasks.convert_genotype_task')

    genotype = Genotype.objects.get(id=genotype_id)

    raw_data = genotype.genotype_file.read().decode('ascii')
    vcf_data = convert(raw_data)

    filename = '{}_genotype.vcf'.format(genotype.profile.id)
    genotype.converted_file.save(name=filename, content=ContentFile(vcf_data))

    genotype.save()

