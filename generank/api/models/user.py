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
