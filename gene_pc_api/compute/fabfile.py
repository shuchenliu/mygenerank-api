""" A series of fabric tasks for remote execution of
the scientific pipeline.
"""

from django.conf import settings
from fabric.api import run, env


env.hosts = settings.REMOTE_HOSTS


def build_pipeline(user_id, profile_id):
    """ Given a user_id and profile_id, generate a given pipeline
    to analyze that user.
    :returns pipeline_id: An identifier cooresponding to the pipeline
    script for the given sample.
    """
    run('')


def submit_pipeline(pipeline_id):
    """ Given a pipeline_id, submit the cooresponding pipeline
    for execution.
    :returns job_id: The pipeline's execution job id.
    """
    run('')
