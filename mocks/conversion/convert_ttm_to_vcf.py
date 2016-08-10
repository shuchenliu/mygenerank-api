#!/bin/python
'''
This file contains mock functions for testing purposes.
'''

def convert(raw_data):
    ''' This function is a mock for the conversion function
    in the pipeline.'''

    vcf_header = '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tGENOTYPE\n'
    vcf_content = vcf_header
    return vcf_content
