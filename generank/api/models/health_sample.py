import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

from .user import User


class HealthSampleIdentifier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.CharField(max_length=150, blank=True, unique=True)

    def __str__(self):
        return '<API: HealthSampleIdentifier: %s>' % self.value


class HealthSample(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='health_samples',
        on_delete=models.CASCADE, blank=True)
    identifier = models.ForeignKey(HealthSampleIdentifier, on_delete=models.CASCADE)
    value = models.FloatField(max_length=100, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    collected_date = models.DateTimeField(default=timezone.now)
    units = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('user', 'identifier', 'value', 'start_date', 'end_date', 'units')

    def __str__(self):
        return '<API: HealthSample: %s %s>' % (self.identifier, self.value)
