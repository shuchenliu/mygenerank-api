from __future__ import absolute_import

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail

from push_notifications.models import APNSDevice

from . import tasks
from .models import User, Activity, ActivityStatus, RiskScore, LifestyleMetric


@receiver(post_save, sender=User)
def create_related_models_for_user(sender, instance, created, **kwargs):
    """ Whenever a user is created, also create any related models. """
    if created:
        tasks.create_statuses_for_new_user.delay(str(instance.id))


@receiver(post_save, sender=LifestyleMetric)
def create_metric_statuses_for_user(sender, instance, created, **kwargs):
    """ Whenever a user is created, also create any related models. """
    if created:
        tasks.create_metric_statuses_for_existing_users.delay(str(instance.id))


@receiver(post_save, sender=Activity)
def create_statuses_for_existing_users(sender, instance, created, **kwargs):
    """ Whenever a new Activity is created, add status objects to
    all existing users.
    """
    if created:
        tasks.create_statuses_for_existing_users.delay(str(instance.id))


@receiver(post_save, sender=Activity)
def send_notification_for_new_activity(sender, instance, created, **kwargs):
    """ Whenever a new Activity is created, send a notification to
    all existing users.
    """
    if created:
        tasks.send_activity_notification.delay(str(instance.id))
