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
