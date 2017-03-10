""" A module for distributing calculation tasks for CAD Risk Score. """
import os, requests, sys, subprocess, uuid

from celery import shared_task, chord, group

from generank.api import models
from generank.api.tasks import send_risk_score_notification, send_post_cad_survey_to_users
from generank.twentythreeandme.models  import User, Profile, Genotype
from generank.compute.contextmanagers import record

sys.path.append(os.environ['PIPELINE_DIRECTORY'].strip())
from analysis import steps

PHENOTYPE = 'cad_160808'
SCORE_RESULTS_ORDER = [
    'custom', 'africans', 'native americans', 'east asians', 'europeans', 'south asians'
]


@shared_task
def _get_cad_haplotypes(user_id, chromosome):
    """ Given a chromosome, determine the known haplotypes inside it. """
    with record('tasks.cad._get_cad_haplotypes', user_id):
        user = User.objects.get(api_user_id=user_id)
        return steps.grs_step_2(uuid.uuid4().hex, user.profile.genotype.converted_file,
            user_id, PHENOTYPE, chromosome)


#@shared_task(bind=True)
#def _dispatch_impute_tasks(self, haps, user_id, chromosome):
#    """ Given a chromosome and it's haplotypes, return the imputation tasks over
#    each chunk for that chromosome. """
#    self.replace(group(_impute_and_get_cad_risk_per_chunk.s(haps, user_id, chunk)
#        for chunk in steps.get_chunks() if chunk[0] == chromosome))


@shared_task
def _impute_and_get_cad_risk_per_chunk(haps, user_id, chunk):
    """ Given a user, the chunk of a chromosome and the known haplotypes for that
    chromosome, calculate their risk for that given chunk. """
    with record('tasks.cad._impute_and_get_cad_risk_per_chunk', user_id):
        return steps.grs_step_3(uuid.uuid4().hex, *haps, PHENOTYPE, *chunk)


@shared_task
def _get_total_cad_risk(results, user_id):
    """ Given the user's ancestry, and their individual risk per chromosome
    per chunk, calculate their total overall risk. """
    with record('tasks.cad._get_total_cad_risk', user_id):
        # A hack to filter out the ancestry record. Celery doesn't guarantee order.
        ancestry = [result for result in results if 'ancestry' in result[1]][0]
        risk_of_risks = [result for result in results if 'ancestry' not in result[1]]

        filename, ancestry_path, ancestry_contents = ancestry
        return (ancestry_contents, *steps.grs_step_4(uuid.uuid4().hex, filename,
            ancestry_path, ancestry_contents, risk_of_risks, user_id, PHENOTYPE))


@shared_task
def _store_results(results, user_id):
    """ Given the results of a user's CAD risk score, store the data. """
    with record('tasks.cad._store_results', user_id):
        ancestries, path, scores = results
        user = models.User.objects.get(id=user_id)
        cad = models.Condition.objects.filter(name__iexact='coronary artery disease')[0]

        for population_name, score in zip(SCORE_RESULTS_ORDER, scores.split('\n')):
            featured = True if population_name == 'custom' else False
            population = models.Population.objects.filter(name__iexact=population_name)[0]
            risk_score = models.RiskScore(user=user, condition=cad, featured=featured,
                population=population, calculated=True, value=float(score))
            risk_score.save()

        for population_name, per_ancestry in zip(SCORE_RESULTS_ORDER, ancestries.split()):
            population = models.Population.objects.filter(name__iexact=population_name)[0]
            ancestry = models.Ancestry(user=user, population=population, value=float(per_ancestry))
            ancestry.save()



@shared_task
def _send_cad_notification(user_id):
    """ Send a Risk Score Notification for the CAD condition.
    Uses the API method for sending notifications. """
    with record('tasks.cad._send_cad_notification', user_id):
        cad = models.Condition.objects.filter(name__iexact='coronary artery disease')[0]
        send_risk_score_notification(user_id, cad.name)


# Public Tasks


@shared_task
def get_ancestry(user_id):
    """ Given an API user id, perform the ancestry calculations on that
    user's genotype data. """
    with record('tasks.cad.get_ancestry', user_id):
        user = User.objects.get(api_user_id=user_id)
        return steps.grs_step_1(uuid.uuid4().hex, user.profile.genotype.converted_file)


@shared_task
def get_cad_risk_score(user_id):
    """ Given an API user id, perform the grs risk score calculations.
    This is the high level pipeline invocation method used to submit all
    subsequent and dependent steps. """
    with record('tasks.cad.get_cad_risk_score', user_id):
        step_1 = get_ancestry.s(user_id)
        steps_2_and_3 = [
            _get_cad_haplotypes.s(user_id, chunk[0]) | _impute_and_get_cad_risk_per_chunk.s(user_id, chunk)
            for chunk in steps.get_chunks()
        ]
        step_4 = _get_total_cad_risk.s(user_id)
        notify_user = (
            _send_cad_notification.si(user_id) | send_post_cad_survey_to_users.si(user_id)
        )

        workflow = chord(
            header=group([step_1, *steps_2_and_3]),
            body=step_4
        ) | _store_results.s(user_id) | notify_user

        workflow.delay()
