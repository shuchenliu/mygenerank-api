from __future__ import absolute_import

from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger

from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist

from push_notifications.models import APNSDevice

from .models import User, Activity, ActivityStatus, RiskScore


logger = get_task_logger(__name__)


# Email Tasks


@shared_task
def send_registration_email_to_user(registration_url, registration_code, user_email):
    """ Given a user and registration information, send a registration
    email to that user.
    """
    logger.debug('tasks.send_registration_email_to_user')
    html = render_to_string('registration_email.html', {
        'url': registration_url,
        'code': registration_code
    })
    logger.info('Sending email to new user: %s' % user_email)
    send_mail(settings.REGISTER_EMAIL_SUBJECT, '', settings.EMAIL_HOST_USER,
        [user_email], fail_silently=False, html_message=html)


# Notification Tasks


@shared_task
def send_risk_score_notification(user_id, condition_name):
    logger.debug('tasks.send_risk_score_notification')
    try:
        device = APNSDevice.objects.get(user__id=user_id)
        device.send_message("Your risk score for {condition} is available.".format(
            condition=condition_name))
        logger.info('Notification sent to user for new risk score: '
            'User <%s> | Condition <%s>' % (user_id, condition_name))
    except ObjectDoesNotExist as e:
        logger.warning("Device for user %s does not exist." % user_id)


@shared_task
def send_activity_notification(activity_id):
    logger.debug('tasks.send_activity_notification')
    activity = Activity.objects.get(id=activity_id)
    # TODO: refactor to use mass_send
    devices = APNSDevice.objects.filter(active=True)
    devices.send_message('A new activity is ready for you!')
    logger.info('New mass activity notification sent to all users.')


# Create New Model Tasks


@shared_task
def create_statuses_for_existing_users(activity_id):
    logger.debug('tasks.create_statuses_for_existing_users')
    activity = Activity.objects.get(id=activity_id)
    for user in User.objects.all():
        status = ActivityStatus(user=user, activity=activity)
        status.save()
    logger.info('New statuses created for existing users.')


@shared_task
def create_statuses_for_new_user(user_id):
    logger.debug('tasks.create_statuses_for_new_user')
    user = User.objects.get(id=user_id)
    activities = [
        Activity.objects.get(study_task_identifier=settings.PHENOTYPE_SURVEY_ID),
        Activity.objects.get(study_task_identifier=settings.GENOTYPE_AUTH_SURVEY_ID)
    ]

    for activity in activities:
        status = ActivityStatus(user=user, activity=activity)
        status.save()
    logger.info('New statuses created for new user: %s' % user_id)


@shared_task
def send_post_cad_survey_to_users(user_id):
    """ On completion of the Risk Score calculation add the Post CAD survey
    status for the user.
    """
    logger.debug('tasks.send_post_cad_survey_to_users')
    user = User.objects.get(id=user_id)
    activity = Activity.objects.get(study_task_identifier=settings.POST_CAD_RESULTS_SURVEY_ID)
    status = ActivityStatus(user=user, activity=activity)
    status.save()
    logger.info('Post CAD survey status created for user: %s' % user_id)


@shared_task
def send_followup_survey_to_users():
    """ Search for any users that have seen their scores for 24wks (~6mo) and
    add a new status for them to complete the followup survey.
    """
    logger.debug('tasks.send_followup_survey_to_users')
    activity = Activity.objects.get(study_task_identifier=settings.POST_CAD_6MO_SURVEY_ID)

    six_months_delta = timedelta(weeks=24)
    date_limit = (date.today() - six_months_delta).strftime("%Y-%m-%d")

    for user in User.objects.all():
        risk_score_is_old_enough = len(RiskScore.objects.filter(
            created_on__lte=date_limit, user=user)) > 0
        user_doesnt_already_have_status = len(ActivityStatus.objects.filter(
            activity=activity, user=user)) == 0

        if risk_score_is_old_enough and user_doesnt_already_have_status:
            follup_status = ActivityStatus(user=user, activity=activity)
            follup_status.save()
            logger.info('Followup survey added for user %s' % user.id)
