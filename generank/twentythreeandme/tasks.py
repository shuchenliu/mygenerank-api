import os, requests, sys

from celery import shared_task, chord, group
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.utils import IntegrityError

from generank import compute

from .models  import User, Profile, Genotype
from .api_client import get_user_info, get_genotype_data


sys.path.append(os.environ['PIPELINE_DIRECTORY'].strip())
from conversion.convert_ttm_to_vcf import convert


logger = get_task_logger(__name__)


@shared_task
def _import_user(token, api_userid):
    """ Given a token and a api_user and a 23andMe profile_id,
    it fetches user data for that profile from 23andMe and saves the user.
    :returns user_info: A dict of the 23andMe User/Profile information.
    """
    logger.debug('tasks.twentythreeandme_delayed_import_task')
    user_info = get_user_info(token)
    ttm_uobj = User.from_json(user_info, token)
    ttm_uobj.user_id = api_userid
    ttm_uobj.save()

    return user_info


@shared_task
def _import_profile(user_info, token, profileid):
    """ Given a token and a user info JSON object this will create a 23andMe
    User. It will also create a Profile object and spawn a job to import the
    genotype data.
    """
    logger.debug('tasks.twentythreeandme_import_task')

    prof = [prof for prof in user_info['profiles']
        if prof['id'] == profileid][0]

    profile = Profile.from_json(prof, ttm_uobj)
    profile.save()

    return str(profile.id)


@shared_task
def _import_genotype(token, profile_id):
    """ Given the id of a profile model and a bearer token, this function will download
    the raw genotype data from 23andme and save it in a genotype object and
    spawns a job to convert the raw file into the VCF format.
    """
    logger.debug('tasks.twentythreeandme_genotype_import_task')
    profile = Profile.objects.get(id=profile_id)
    genotype_data = get_genotype_data(token, profile)
    genotype = Genotype.from_json(genotype_data, profile)
    genotype.save()

    return str(genotype.id)


@shared_task
def _convert_genotype(genotype_id):
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


# Public Tasks

@shared_task
def import_account(token, api_user_id, profile_id, run_after=True):
    """ Import a given user's account details using the OAuth token
    and save the profile under the given API User ID.

    By default, this workflow initiates the computation for all
    risk scores once complete. """
    workflow = (
        _import_user.s(token, api_userid) |
        _import_profile.s(token, profile_id) |
        _import_genotype.si(token, profile_id) |
        _convert_genotype.s()
    )

    if run_after:
        workflow = workflow | compute.tasks.run_all.si(api_user_id)

    workflow.delay()

