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

    def is_complete(self):
        """ Returns true if a user model is ready to be imported. """
        return self.profile_id and self.auth_code and self.user_id

    def __str__(self):
        return '<API: User: %s' % self.email


class Phenotypes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, related_name='phenotypes',
        on_delete=models.CASCADE, blank=True)

    age = models.IntegerField()
    sex = models.CharField(max_length=100)
    smoking_status = models.BooleanField()
    total_cholesterol = models.DecimalField(decimal_places=2, max_digits=5)
    hdl_cholesterol = models.DecimalField(decimal_places=2, max_digits=5)
    systolic_blood_pressure = models.DecimalField(decimal_places=2, max_digits=5)
    taking_blood_pressure_medication = models.BooleanField()

    def __str__(self):
        return '<API: Phenotypes: %s' % self.user.email


class RiskScores(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, related_name='risk_scores',
        on_delete=models.CASCADE, blank=True)

    framingham_score = models.DecimalField(decimal_places=2, max_digits=5)

    def __str__(self):
        try:
            return '<API: RiskScores: %s' % self.user.email
        except:
            return ''


# Signals


@receiver(post_save)
def check_should_import(sender, instance, **kwargs):
    """ After a user is saved, check if it is complete
    If so: kick off the import task.
    """
    try:
        if instance.is_complete():
            profile = Profile.objects.filter(profile_id=instance.profile_id)
            if len(profile) == 0:
                # TODO Integrate Celery
                genome_import_task(instance.user_id, instance.profile_id,
                    instance.auth_code)
    except (AttributeError, IndexError):
        pass
