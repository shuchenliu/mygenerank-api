""" A series of fabric tasks for remote execution of
the scientific pipeline.
"""

import os, sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(),
                os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from settings import REMOTE_HOSTS, PIPELINE_DIRECTORY
from fabric.api import run, env
from io import StringIO
import time

env.hosts = REMOTE_HOSTS

env.shell = '/bin/bash'
def build_cad_grs_pipeline(data_file):
    """ Given a VCF data file, generate a given CAD GRS pipeline
    to analyze that user.
    :returns pipeline_id: An identifier cooresponding to the pipeline
    script for the given sample.
    """
    pipeline_id = 'cad_grs_%s.pipe' % time.time()
    pipeline_builder = os.path.join(PIPELINE_DIRECTORY,'analysis',
                                            'cad_grs_pipeline.py')
    command = (' ').join(['python',pipeline_builder,data_file,pipeline_id])
    run(command, shell= False)

    return pipeline_id

def run_cad_grs_pipeline(data_file):
    """ Given a pipeline_id, submit the cooresponding pipeline
    for execution.
    :returns grs_Score: The pipeline's result.
    """
    pipe_id = build_cad_grs_pipeline(data_file)
    output = run(pipe_id)

    print(output)
