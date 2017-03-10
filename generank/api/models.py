import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registered = models.BooleanField(default=False, blank=False)
    registration_code = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return '<API: User: %s>' % self.username


class ConsentPDF(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='consent_pdfs',
        on_delete=models.CASCADE)

    fs = FileSystemStorage(location=settings.CONSENT_FILE_LOCATION,
        base_url=settings.CONSENT_FILE_URL)
    consent_pdf = models.FileField(storage=fs)
    name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return '<Consent: %s %s>' % (self.user.username, self.consent_pdf)


class Signature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consent_pdf = models.OneToOneField(ConsentPDF, on_delete=models.CASCADE)
    consent_signed = models.BooleanField(default=False)
    date_signed = models.DateField()

    def __str__(self):
        return '<Signature: %s %s>' % (self.consent_pdf.user.username, self.consent_signed)


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

    class Meta:
        unique_together = ('user', 'population')

    def __str__(self):
        return '<API: Ancestry: %s %s %s>' % (self.user.email, self.population.name,
            self.value)


class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    subtitle = models.CharField(max_length=100, blank=True)
    study_task_identifier = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=100, blank=True)

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
        return '<API: ActivityStatus: %s %s>' % (self.user.username,
            self.activity.study_task_identifier)


class ActivityAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_identifier = models.CharField(max_length=100, blank=True)
    value = models.CharField(max_length=1000, blank=True)
    activity = models.ForeignKey(Activity, related_name='activity_answers',
        on_delete=models.CASCADE, blank=True)
    user = models.ForeignKey(User, related_name='activity_answers',
        on_delete=models.CASCADE, blank=True)

    class Meta:
        unique_together = ('user', 'question_identifier', 'activity')

    def __str__(self):
        return '<API: ActivityAnswer: %s %s>' % (self.user.username, self.question_identifier)


class HealthSample(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='health_samples',
        on_delete=models.CASCADE, blank=True)
    identifier = models.CharField(max_length=100, blank=True)
    value = models.FloatField(max_length=100, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    collected_date = models.DateTimeField(default=timezone.now)
    units = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('user', 'identifier', 'value', 'start_date', 'end_date', 'units')

    def __str__(self):
        return '<API: HealthSample: %s %s>' % (self.identifier, self.value)


class ActivityScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='activity_score',
        on_delete=models.CASCADE, blank=True)
    value = models.FloatField(max_length=100, blank=True)
    delta = models.FloatField(max_length=100, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '<API: ActivityScore: %s %s>' % (self.user.username, self.value)
