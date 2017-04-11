import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

from .user import User
from .health_sample import HealthSampleIdentifier
from .activity import Activity
from .condition import Condition


class LifestyleMetric(models.Model):
    name = models.CharField(max_length=150, blank=True, unique=True)
    identifier = models.CharField(max_length=150, blank=True, unique=True)

    def __str__(self):
        return '<API: LifestyleMetric: %s>' % (self.name,)


class LifestyleMetricSeries(models.Model):
    health_sample_identifiers = models.ManyToManyField(HealthSampleIdentifier, blank=True)
    activities = models.ManyToManyField(Activity, blank=True)
    conditions = models.ManyToManyField(Condition, blank=True)
    metric = models.ManyToManyField(LifestyleMetric, blank=True, related_name='series')
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return '<API: LifestyleMetricSeries: %s>' % (self.name,)


class LifestyleMetricScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    series = models.ForeignKey(LifestyleMetricSeries, related_name='values',
        on_delete=models.CASCADE, blank=True)
    value = models.FloatField(max_length=100, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    is_personal_best = models.BooleanField(default=False)

    def __str__(self):
        return '<API: LifestyleMetricScore: %s, %s, %s>' % (self.series.name,
            self.user.username, self.value)


class LifestyleMetricGoal(models.Model):
    metric = models.ForeignKey(LifestyleMetric, related_name='goals',
        on_delete=models.CASCADE, blank=True)
    series = models.ForeignKey(LifestyleMetricSeries, related_name='goals',
        on_delete=models.CASCADE, blank=True)
    conditions = models.ManyToManyField(Condition, blank=True)
    value = models.FloatField(max_length=100, blank=True)
    name = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return '<API: LifestyleMetricGoal: %s, %s>' % (self.metric.name, self.name)


class LifestyleMetricStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    metric = models.ForeignKey(LifestyleMetric, related_name='status',
        on_delete=models.CASCADE, blank=True)
    last_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('metric', 'user')

    def __str__(self):
        return '<API: LifestyleMetricStatus: %s, %s>' % (self.user.username, self.last_updated)
