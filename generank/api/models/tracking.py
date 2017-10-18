import uuid, sys, os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

from .user import User


class TrackedEvent(models.Model):
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
