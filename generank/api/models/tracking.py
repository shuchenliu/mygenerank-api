import uuid, sys, os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

from .user import User


class TrackedEvent(models.Model):
    """ A tracked event represents any in-ap,p user initiated task that is worth
    tracking for behavioral study purposes. Typically these events are things like
    a certain page has appeared, or a certain set of buttons were tapped.

    Events can be sent without a user (i.e. before a user account is created) and
    are stored without that information. This is useful for dropoff analysis during
    things like consent.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    view = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(
        User, related_name='tracked_events', on_delete=models.CASCADE,
        null=True, blank=True
    )
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        view = self.view if self.view is not None else 'None'
        return '{view}: {name}'.format(view=view, name=self.name)
