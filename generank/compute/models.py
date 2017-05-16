import uuid

from django.db import models

from generank.api import models as api


class TaskStatus(models.Model):
    """ A record of the status of a task at a given point in time. """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(api.User, related_name='task_statuses',
        on_delete=models.CASCADE, null=True, blank=True)
    identifier = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=100, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        username = self.user.username if self.user is not None else 'system'
        return '<Compute TaskStatus: %s %s -- %s' % (self.identifier,
            username, self.status)
