from celery import shared_task

from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist

from push_notifications.models import APNSDevice

from .models import User, Activity, ActivityStatus, RiskScore


@shared_task
def send_registration_email_to_user(registration_url, registration_code, user_id, user_email):
    html = render_to_string('registration_email.html', {
        'url': registration_url,
        'code': registration_code
    })
    send_mail(settings.REGISTER_EMAIL_SUBJECT, '', settings.EMAIL_HOST_USER,
        [user_email], fail_silently=False, html_message=html)


@shared_task
def send_risk_score_notification(user_id, condition_name):
    try:
        device = APNSDevice.objects.get(user__id=user_id)
        device.send("Your risk score for {condition} is available.".format(
            condition=condition_name))
    except ObjectDoesNotExist:
        print("Device for user %s does not exist." % user_id)


@shared_task
def send_activity_notification(activity_id):
    # TODO: refactor to use mass_send
    devices = GCMDevice.objects.filter(active=True)
    devices.send_message('A new activity is ready for you!')


@shared_task
def create_statuses_for_existing_users(activity_id):
    for user in User.objects.all():
        status = ActivityStatus(user=user, activity__id=activity_id)
        status.save()


@shared_task
def create_statuses_for_new_user(user_id):
    for activity in Activity.objects.all():
        status = ActivityStatus(user__id=user_id, activity=activity)
        status.save()
