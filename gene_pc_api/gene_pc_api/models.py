import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files.storage import FileSystemStorage

from rest_framework.authtoken.models import Token


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registered = models.BooleanField(default=False, blank=False)
    registration_code = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return '<API: User: %s>' % self.email


class ConsentPDF(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='consent_pdfs',
        on_delete=models.CASCADE)

    fs = FileSystemStorage(location=settings.CONSENT_FILE_LOCATION,
        base_url=settings.CONSENT_FILE_URL)
    consent_pdf = models.FileField(storage=fs)

    def __str__(self):
        return '<Consent: %s %s>' % (self.user.email, self.consent_pdf)


class Signature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(ConsentPDF, on_delete=models.CASCADE)
    consent_signed = models.BooleanField(default=False)
    date_signed = models.DateField()

    def __str__(self):
        return '<Signature: %s %s>' % (self.user.email, self.consent_signed)


class Condition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    overview = models.CharField(max_length=1024, blank=True)
    description = models.CharField(max_length=1024, blank=True)

    def __str__(self):
        return '<API: Condition: %s>' % self.name


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
        on_delete=models.PROTECT)
    condition = models.ForeignKey(Condition, related_name='risk_scores',
        on_delete=models.PROTECT)
    population = models.ForeignKey(Population, related_name='risk_scores',
        on_delete=models.PROTECT)
    calculated = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'condition', 'population')

    def __str__(self):
        return '<API: RiskScore: %s %s %s>' % (self.user.email, self.condition,
            self.population)


class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    subtitle = models.CharField(max_length=100, blank=True)
    study_task_identifier = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return '<API: Activity: %s>' % (self.name)


class ActivityStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='activity_statuses',
        on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, related_name='activity_statuses',
        on_delete=models.CASCADE)
    complete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'activity')

    def __str__(self):
        return '<API: ActivityStatus: %s %s>' % (self.user.email,
            self.activity.study_task_identifier)


class ActivityAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_identifier = models.CharField(max_length=100, blank=True)
    value = models.CharField(max_length=1000, blank=True)
    activity = models.ForeignKey(Activity, related_name='activity_answers',
        on_delete=models.PROTECT, blank=True)
    user = models.ForeignKey(User, related_name='activity_answers',
        on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return '<API: ActivityAnswer: %s %s>' % (self.user.email, self.question_identifier)
