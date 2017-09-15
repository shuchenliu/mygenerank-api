# MyGeneRank API

*A research study by the Scripps Translational Science Institute*

[Visit our site and get started with the study.](https://mygenerank.scripps.edu)

[![Build Status](https://travis-ci.org/TorkamaniLab/mygenerank-api.svg?branch=master)](https://travis-ci.org/TorkamaniLab/mygenerank-api)
[![Coverage Status](https://coveralls.io/repos/github/TorkamaniLab/mygenerank-api/badge.svg?branch=master)](https://coveralls.io/github/TorkamaniLab/mygenerank-api?branch=master)

## Introduction

This repository contains the Django-REST API and wrapper for the computation layer of MyGeneRank, a study run by the Scripps Translational Science Institute.


## About the Study

The goal of this study is to determine how your genetic risk influences health decisions and other things that can be controlled in life. Our first genetic risk score is calculated for coronary artery disease (CAD).


## Development and Running the Tests

It's recommended to run the MyGeneRank API in a [virtual environment][venv]. This tutorial will assume you've already set that up.

[venv]: http://virtualenvwrapper.readthedocs.io/en/latest/

**Note:** This repository does not contain any of the actual calculations for the Genetic Risk Scores or Combined Lifestyle Risk Scores. It requires an external module (supplied by the `PIPELINE_DIRECTORY` environment variable). By default the API will use it's own Mock Pipeline for development purposes.


### Environment

There are a few environment variables you'll need to set to use MyGeneRank's API locally.


#### Email Settings

- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`


#### Reddit Settings

- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USERNAME`
- `REDDIT_PASSWORD`


#### Twenty Three and Me Settings

- `TTM_CLIENT_ID`
- `TTM_CLIENT_SECRET`
- `TTM_GRANT_TYPE`
- `TTM_REDIRECT_URI`
- `TTM_SCOPE`


#### Misc Settings

- `PIPELINE_DIRECTORY`
- `APNS_CERTIFICATE`
- `SECRET_KEY`


### Initial Setup

Tests are run using `nose`. Installing the project's dev dependencies will install everything needed to run the tests.

```bash
$ git clone https://github.com/TorkamaniLab/gene-pc-api.git && cd gene-pc-api
$ pip install -r dev_requirements.txt
$ pip install -r requirements.txt
$ ./manage.py migrate
$ ./manage.py test
```

Congrats! You've got a running development version of MyGeneRank's API.


### Code Coverage

To measure code coverage in MyGeneRank, run the following command to generate an HTML report of the current code coverage.

```bash
$ coverage run --branch --source=generank ./manage.py test && coverage html
```
