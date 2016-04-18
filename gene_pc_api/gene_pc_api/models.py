import uuid

from django.db import models

# Create your models here.

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    token = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
