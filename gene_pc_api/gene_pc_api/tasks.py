from celery import shared_task

from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.reverse import reverse
from rest_framework.request import Request

from push_notifications.models import APNSDevice

from .models import User, Activity, ActivityStatus, RiskScore


@shared_task
def send_registration_email_to_user(request, user):
    url = reverse('api:user-register', kwargs={'pk': user.id})
    html = render_to_string('registration_email.html', {
        'url': request.build_absolute_uri(url),
        'code': user.registration_code
    })
    send_mail(settings.REGISTER_EMAIL_SUBJECT, '', settings.EMAIL_HOST_USER,
        [user.email], fail_silently=False, html_message=html)


@shared_task
def send_risk_score_notification(risk_score):
    try:
        device = APNSDevice.objects.get(user__id=risk_score.user.id)
        device.send("Your risk score for {condition} is available.".format(
            condition=risk_score.condition.name))
    except ObjectDoesNotExist:
        print("Device for user %s does not exist." % risk_score.user.id)

@shared_task
def send_activity_notification(activity):
    devices = GCMDevice.objects.filter(active=True)
    devices.send_message('A new activity is ready for you!')


@shared_task
def create_statuses_for_existing_users(activity):
    for user in User.objects.all():
        status = ActivityStatus(user=user, activity=activity)
        status.save()


@shared_task
def create_statuses_for_new_user(user):
    for activity in Activity.objects.all():
        status = ActivityStatus(user=user, activity=activity)
        status.save()
