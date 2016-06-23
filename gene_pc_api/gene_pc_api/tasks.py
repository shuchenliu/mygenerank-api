from celery import shared_task

from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_registration_email_to_user(user):
    url = reverse('api:user-register', kwargs={'pk': user.id})
    html = render_to_string('registration_email.html', {'url': url})
    send_mail(settings.REGISTER_EMAIL_SUBJECT, '', settings.EMAIL_HOST_USER,
        [user.email], fail_silently=False, html_message=html)


@shared_task
def send_risk_score_notification(risk_score):
    device = APNSDevice.objects.get(user__id=risk_score.user.id)
    device.send("Your risk score for {condition} is available.".format(
        condition=risk_score.condition.name))


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
