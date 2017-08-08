from __future__ import absolute_import

from datetime import timedelta

from celery import shared_task

from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from push_notifications.models import APNSDevice

from generank.compute.contextmanagers import record
from .models import User, Activity, ActivityStatus, RiskScore


# Email Tasks


@shared_task
def send_registration_email_to_user(registration_url, registration_code, user_email):
    """ Given a user and registration information, send a registration
    email to that user.
    """
    with record('tasks.api.send_registration_email_to_user'):
        html = render_to_string('registration_email.html', {
            'url': registration_url,
            'code': registration_code
        })
        send_mail(settings.REGISTER_EMAIL_SUBJECT, '', settings.EMAIL_HOST_USER,
            [user_email], fail_silently=False, html_message=html)


# Notification Tasks


@shared_task
def send_risk_score_notification(user_id, condition_name):
    with record('tasks.api.send_risk_score_notification', user_id):
        message = 'Your risk score for {condition} is available.'.format(
            condition=condition_name)
        # APNS
        devices = APNSDevice.objects.filter(active=True, user__is_active=True, user__id=user_id)
        devices.send_message(message)
        # Email
        user = User.objects.get(id=user_id)
        html = render_to_string('new_risk_score.html', {
            'condition_name': condition_name
        })
        send_mail(message, message, settings.EMAIL_HOST_USER,
            [user.email], fail_silently=False, html_message=html)


@shared_task
def send_activity_notification(activity_id):
    with record('tasks.api.send_activity_notification'):
        message = 'A new activity is ready for you!'
        # APNS
        activity = Activity.objects.get(id=activity_id)
        devices = APNSDevice.objects.filter(active=True, user__is_active=True)
        devices.send_message(message)
        # Email
        for user in User.objects.filter(is_active=True):
            html = render_to_string('new_activity.html', {})
            send_mail(message, message, settings.EMAIL_HOST_USER,
                [user.email], fail_silently=False, html_message=html)


# Create New Model Tasks


@shared_task
def create_statuses_for_existing_users(activity_id):
    with record('tasks.api.create_statuses_for_existing_users'):
        activity = Activity.objects.get(id=activity_id)
        if activity.is_tracked_serverside:
            for user in User.objects.filter(is_active=True):
                status = ActivityStatus(user=user, activity=activity)
                status.save()


@shared_task
def create_statuses_for_new_user(user_id):
    with record('tasks.api.create_statuses_for_new_user', user_id):
        user = User.objects.get(id=user_id)
        if not user.is_active:
            return
        activities = [
            Activity.objects.get(study_task_identifier=study_id)
            for study_id in settings.DEFAULT_STUDY_IDS
        ]

        for activity in activities:
            if activity.is_tracked_serverside:
                status = ActivityStatus(user=user, activity=activity)
                status.save()


@shared_task
def send_post_cad_survey_to_users(user_id):
    """ On completion of the Risk Score calculation add the Post CAD survey
    status for the user.
    """
    with record('tasks.api.send_post_cad_survey_to_users', user_id):
        user = User.objects.get(id=user_id)
        if not user.is_active:
            return
        activity = Activity.objects.get(study_task_identifier=settings.POST_CAD_RESULTS_SURVEY_ID)
        status = ActivityStatus(user=user, activity=activity)
        status.save()


@shared_task
def send_followup_survey_to_users():
    """ Search for any users that have seen their scores for 24wks (~6mo) and
    add a new status for them to complete the followup survey.
    """
    with record('tasks.api.send_followup_survey_to_users'):
        activity = Activity.objects.get(study_task_identifier=settings.POST_CAD_6MO_SURVEY_ID)

        six_months_delta = timedelta(weeks=24)
        date_limit = (timezone.now() - six_months_delta).strftime("%Y-%m-%d")

        for user in User.objects.filter(is_active=True):
            risk_score_is_old_enough = len(RiskScore.objects.filter(
                created_on__lte=date_limit, user=user)) > 0
            user_doesnt_already_have_status = len(ActivityStatus.objects.filter(
                activity=activity, user=user)) == 0

            if risk_score_is_old_enough and user_doesnt_already_have_status:
                follup_status = ActivityStatus(user=user, activity=activity)
                follup_status.save()
