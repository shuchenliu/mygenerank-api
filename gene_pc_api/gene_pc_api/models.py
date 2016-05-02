import uuid

from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save

from gene_pc_api.twentythreeandme.models import Profile
from gene_pc_api.twentythreeandme.tasks import genome_import_task


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # 23andMe API keys
    user_id = models.CharField(max_length=100, blank=True)
    profile_id = models.CharField(max_length=100, blank=True)
    auth_code = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("user_id", "profile_id")

    @property
    def is_complete(self):
        """ Returns true if a user model is ready to be imported. """
        return (len(self.profile_id) > 0 and len(self.auth_code) > 0 and
            len(self.user_id) > 0)

    def __str__(self):
        return '<API: User: %s' % self.email


class CommomnInfo(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    value = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=1024, blank=True)

    DATA_TYPES = (
        ('str', 'string'),
        ('float', 'floating point nunber'),
        ('int', 'integer'),
        ('bool', 'boolean')
    )
    datatype = models.CharField( max_length=10, blank=True, choices = DATA_TYPES)

    class Meta:
        abstract = True

class Phenotypes(CommomnInfo):
    user = models.ForeignKey(User, related_name='phenotypes',
        on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return '<API: Phenotype: %s %s' % (self.user.email, self.name)


class RiskScores(CommomnInfo):
    user = models.ForeignKey(User, related_name='risk_scores',
        on_delete=models.PROTECT, blank=True)
    calculated = models.BooleanField(default = False)

    def __str__(self):
        try:
            return '<API: RiskScore: %s %s' % (self.user.email, self.name)
        except:
            return ''


class Activities(models.Model):
    user = models.ForeignKey(User, related_name='activities',
        on_delete=models.CASCADE, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    subtitle = models.CharField(max_length=100, blank=True)
    complete = models.BooleanField(default = False)

    def __str__(self):
        try:
            return '<API: Activity: %s %s' % (self.user.email, self.name)
        except:
            return ''


# Signals


@receiver(post_save)
def check_should_import(sender, instance, **kwargs):
    """ After a user is saved, check if it is complete
    If so: kick off the import task.
    """
    try:
        if instance.is_complete:
            profile = Profile.objects.filter(profile_id=instance.profile_id)
            if len(profile) == 0:
                pass
                # TODO Integrate Celery
                #genome_import_task.delay(instance.user_id, instance.profile_id,
                #    instance.auth_code)
    except (AttributeError, IndexError):
        pass
