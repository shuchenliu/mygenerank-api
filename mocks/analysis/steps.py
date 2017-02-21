""" Mocks for the analysis steps. """


def get_chunks():
    return [[1,2,3,4,5]]


def grs_step_1(user_id, vcf_file, shell=False, timeout=5, check=True):
    return ('some id 1', 'some/ancestry/path', '0.01 0.02 0.03 0.03 0.3\n')


def grs_step_2(id, vcf_file, user_id, phenotype, chromosome, shell=False,
        timeout=180, check=True):
    return ('some_id_2', 'some/file/path', 'some data from the file')


def grs_step_3(id, vcf_filename, pre_haps_filepath, pre_haps_data, phenotype,
        chromosome, chunk, start, stop, shell=False, timeout=180, check=True):
    return ('some_id_3', 'some/file/path', 'some data from the file')


def grs_step_4(id, vcf_filename, ancestry_path, ancestry_contents, grs_paths_and_contents,
        user_id, phenotype, shell=False, timeout=180, check=True):
    return '/path/to/score', '0.0001\n0.02\n0.1\n0.0003\n0.32\n0.78'
