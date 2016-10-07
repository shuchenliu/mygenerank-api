""" A module for distributing calculation tasks for CAD Risk Score. """
import os, requests, sys, subprocess, uuid

from celery import shared_task, chord, group
from celery.utils.log import get_task_logger

from generank.twentythreeandme.models  import User, Profile, Genotype

sys.path.append(os.environ['PIPELINE_DIRECTORY'].strip())
from analysis import steps


logger = get_task_logger(__name__)
PHENOTYPE = 'cad_160808'


@shared_task
def _get_cad_haplotypes(user_id, chromosome):
    """ Given a chromosome, determine the known haplotypes inside it. """
    logger.debug('tasks.cad._get_cad_haplotypes')
    user = User.objects.get(user_id=user_id)
    return steps.grs_step_2(uuid.v4().hex, user.profile.genotype.converted_file,
        user_id, PHENOTYPE, chromosome)


@shared_task
def _impute_and_get_cad_risk_per_chunk(user_id, chunk, haps_path, haps_data):
    """ Given a user, the chunk of a chromosome and the known haplotypes for that
    chromosome, calculate their risk for that given chunk.
    """
    logger.debug('tasks.cad._impute_and_get_cad_risk_per_chunk')
    vcf_filename = None
    steps.grs_step_3(uuid.v4().hex, vcf_filename, haps_path, haps_data, *chunk)


@shared_task
def _get_generic_risk(haps_path, haps_data, user_id, chromosome):
    """ Calculate the risk scores for each chunk in a given chromosome. """
    logger.debug('tasks.cad._get_generic_risk')
    return group(
        _impute_and_get_cad_risk_per_chunk.s(user_id, chunk, haps_path, haps_data)
        for chunk in steps.get_chunks()
            if chunk[0] == chr
    ).get()


@shared_task
def _get_total_cad_risk(ancestry_path, ancestry_contents, risk_of_risks, user_id):
    """ Given the user's ancestry, and their individual risk per chromosome
    per chunk, calculate their total overall risk.
    """
    logger.debug('tasks.cad._get_total_cad_risk')
    vcf_filename = None
    risks = [risk for chr_risks in risk_of_risks for risk in chr_risks]
    return steps.grs_step_4(uuid.v4().hex, vcf_filename, ancestry_path, ancestry_contents,
        risks, user_id)


# Public Tasks


@shared_task
def get_ancestry(user_id):
    """ Given an API user id, perform the ancestry calculations on that
    user's genotype data. """
    logger.debug('tasks.cad.get_ancestry')
    user = User.objects.get(user_id=user_id)
    return steps.grs_step_1(user_id, user.profile.genotype.converted_file)


@shared_task
def get_cad_risk_score(user_id):
    """ Given an API user id, perform the grs risk score calculations.
    This is the high level pipeline invocation method used to submit all
    subsequent and dependent steps.
    """
    logger.debug('tasks.cad.get_cad_risk_score')
    chromosomes = steps.get_chunks()

    workflow = chord([
        # Step 1
        get_ancestry.s(user_id),
        # Steps 2 & 3
        group((
            _get_cad_haplotypes.s(user_id, chr) | _get_generic_risk.s(user_id, chr)
        ) for chr in chromosomes)
    # Step 4 (once they're done)
    ])(_get_total_cad_risk.s(user_id))

    return workflow().get()
