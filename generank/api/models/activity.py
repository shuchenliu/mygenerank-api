import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

from .user import User


class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    subtitle = models.CharField(max_length=100, blank=True)
    study_task_identifier = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=100, blank=True)
    is_tracked_serverside = models.BooleanField(default=True)

    def __str__(self):
        return '<API: Activity: %s>' % (self.name)


class ActivityStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='activity_statuses',
        on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, related_name='activity_statuses',
        on_delete=models.CASCADE)
    complete = models.BooleanField(default=False)
    created_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'activity', 'created_on')

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
    created_on = models.DateTimeField(default=timezone.now)

    @property
    def boolean_value(self):
        if(self.value.lower() == "true" or self.value.lower() == "yes"):
            return True
        elif(self.value.lower() == "false" or self.value.lower() == "no"):
            return False
        else:
            raise ValueError

    def __str__(self):
        return '<API: ActivityAnswer: %s %s>' % (self.user.username, self.question_identifier)
