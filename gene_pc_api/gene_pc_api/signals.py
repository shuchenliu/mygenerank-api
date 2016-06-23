from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail

from .models import User, Activity, ActivityStatus
from .tasks import send_registration_email_to_user


@receiver(post_save, sender=User)
def create_related_models_for_user(sender, instance, created, **kwargs):
    """ Whenever a user is created, also create any related models. """
    if created:
        for activity in Activity.objects.all():
            status = ActivityStatus(user=instance, activity=activity)
            status.save()


@receiver(post_save, sender=User)
def send_registration_email_for_new_user(sender, instance, created, **kwargs):
    """ When a new user is created, send an registration email. """
    if created:
        send_registration_email_to_user.delay(instance)


@receiver(post_save, sender=Activity)
def create_status_for_old_users(sender, instance, created, **kwargs):
    """ Whenever a new Activity is created, add status objects to
    all existing users.
    """
    if not created:
        return
    for user in User.objects.all():
        status = ActivityStatus(user=user, activity=instance)
        status.save()
