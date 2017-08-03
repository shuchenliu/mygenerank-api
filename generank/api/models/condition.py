import uuid, sys, os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

from .user import User


class Condition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    overview = models.CharField(max_length=1024, blank=True)
    description = models.CharField(max_length=1024, blank=True)
    risk_explanation = models.CharField(max_length=5024, blank=True)
    multiple_scores_explanation = models.CharField(max_length=5024, blank=True)
    supporting_evidence = models.CharField(max_length=5024, blank=True)
    follow_up_activity_identifier = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return '<API: Condition: %s>' % self.name

    @property
    def is_modifiable_by_behavior(self):
        """ Returns whether or not a given condition has the ability to be
        modified by behavior or not.

        Note:
        Just because a given condition *can* have be modified by behavior
        does not mean that the user has completed the requirements to
        perform the modifications.
        """
        return self.reductors.count() > 0


class Population(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return '<API: Population: %s>' % self.name


class RiskScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    value = models.FloatField(max_length=100, blank=True, default=-1.0)
    description = models.CharField(max_length=1024, blank=True)
    user = models.ForeignKey(User, related_name='risk_scores',
        on_delete=models.CASCADE)
    condition = models.ForeignKey(Condition, related_name='risk_scores',
        on_delete=models.CASCADE)
    population = models.ForeignKey(Population, related_name='risk_scores',
        on_delete=models.CASCADE)
    calculated = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    created_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'condition', 'population')

    def __str__(self):
        return '<API: RiskScore: %s %s %s>' % (self.user.username, self.condition,
            self.population)


class Ancestry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.FloatField(max_length=100, blank=True, default=-1.0)
    user = models.ForeignKey(User, related_name='ancestry',
        on_delete=models.CASCADE)
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'population')

    def __str__(self):
        return '<API: Ancestry: %s %s %s>' % (self.user.email, self.population.name,
            self.value)


class RiskReductor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    identifier = models.CharField(unique=True, max_length=100, blank=True)
    condition = models.ForeignKey(Condition, related_name='reductors',
        on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=timezone.now)
    description = models.TextField(max_length=800, blank=True)

    def __str__(self):
        return '<API: RiskReductor: %s %s>' % (self.name, self.identifier)


class RiskReductorOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    identifier = models.CharField(unique=True, max_length=100, blank=True)
    value = models.FloatField(max_length=100, blank=True, default=-1.0)
    reductor = models.ForeignKey(RiskReductor, related_name='options',
        on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '<API: RiskReductorOption: %s %s>' % (self.name, self.identifier)

