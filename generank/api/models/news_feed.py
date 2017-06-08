import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Item(models.Model):
    """ An model that represents an item in the global news feed. These models
    will have various extensions added to them with additional data depending
    on their source.
    """
    SOURCES = {
        'reddit': 0,
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.IntegerField()
    link = models.URLField()
    title = models.CharField(max_length=300)
    image = models.URLField(null=True, blank=True)
    description = models.CharField(max_length=450, null=True, blank=True)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '<Item: %s>' % self.title
