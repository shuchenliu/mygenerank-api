from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail

from push_notifications.models import APNSDevice

from .models import User, Activity, ActivityStatus, RiskScore
from .tasks import send_registration_email_to_user, \
    create_statuses_for_new_user, create_statuses_for_existing_users, \
    send_risk_score_notification, send_activity_notification


@receiver(post_save, sender=User)
def create_related_models_for_user(sender, instance, created, **kwargs):
    """ Whenever a user is created, also create any related models. """
    if created:
        create_statuses_for_new_user.delay(instance.id)


@receiver(post_save, sender=Activity)
def create_statuses_for_existing_users(sender, instance, created, **kwargs):
    """ Whenever a new Activity is created, add status objects to
    all existing users.
    """
    if created:
        create_statuses_for_existing_users.delay(instance.id)


@receiver(post_save, sender=RiskScore)
def send_nofitication_for_new_risk_score(sender, instance, created, **kwargs):
    """ Whenever a new risk score is created for a given user, send them
    a notification to let them know.
    """
    if created:
        send_risk_score_notification.delay(instance.user.id,
            instance.condition.name)


@receiver(post_save, sender=Activity)
def send_notification_for_new_activity(sender, instance, created, **kwargs):
    """ Whenever a new Activity is created, send a notification to
    all existing users.
    """
    if created:
        send_activity_notification.delay(instance.id)
