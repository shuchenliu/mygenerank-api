import uuid

from django.conf import settings
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.utils import timezone
#import logging


class Settings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grant_type = models.CharField(max_length=100)
    response_type = models.CharField(max_length=10)
    client_id = models.CharField(max_length=500)
    client_secret = models.CharField(max_length=500)
    redirect_uri = models.URLField()
    scope = models.CharField(max_length=150)


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=100, blank=True, editable=False)
    profile_id = models.CharField(max_length=100, blank=True, editable = False)
    email = models.EmailField(null=True, blank=True, editable=True)
    created_on = models.DateTimeField(default=timezone.now)

    ## API user properties
    api_user_id = models.UUIDField(blank=True, editable=False, null = True, unique=True)

    resource_url = 'https://api.23andme.com/1/user/'

    def __str__(self):
        return '<TwentyThreeAndMe: User: %s>' % self.api_user_id

    @staticmethod
    def from_json(data):
        return User(user_id=data['id'], email=data.get('email', None))


class APIToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    access_token = models.CharField(max_length=100)
    token_type = models.CharField(max_length=100)
    expires_in = models.IntegerField()
    refresh_token = models.CharField(max_length=100)
    scope = models.CharField(max_length=150)

    def __str__(self):
        return '<TwentyThreeAndMe: Token: %s>' % self.id

    @staticmethod
    def from_json(data, user):
        print(data)
        return APIToken(user=user, **data)


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE,
         blank=True, null=True)
    profile_id = models.CharField(max_length=100)
    genotyped = models.BooleanField(blank=True)
    created_on = models.DateTimeField(default=timezone.now)

    resource_url = 'https://api.23andme.com/1/user/{}/'

    @property
    def has_imported(self):
        """ Whether or not a given user has been imported. """
        return not self.profile_id and self.genotype.genotype_file_url

    def __str__(self):
        return '<TwentyThreeAndMe: Profile: %s>' % self.user.email


    @staticmethod
    def from_json(profile_data, user):
        profile = Profile(
            user = user,
            genotyped = profile_data['genotyped'],
            profile_id = profile_data['id']
        )
        return profile


class Genotype(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE,
        blank=True)

    fs_raw = FileSystemStorage(location=settings.TTM_RAW_STORAGE,
        base_url=settings.TTM_RAW_URL)
    fs_con = FileSystemStorage(location=settings.TTM_CONVERTED_STORAGE,
        base_url=settings.TTM_CONVERTED_URL)
    genotype_file = models.FileField(storage=fs_raw)
    converted_file = models.FileField(storage=fs_con)
    created_on = models.DateTimeField(default=timezone.now)

    resource_url = 'https://api.23andme.com/1/genomes/{profile_id}/'

    @property
    def genotype_file_url(self):
        return self.genotype_file.url

    def __str__(self):
        return '<TwentyThreeAndMe: Genotype: %s>' % self.profile.id

    @staticmethod
    def from_json(data,profile):
        genotype_data = data['genome']
        genotype = Genotype()
        genotype.profile = profile
        genotype.genotype_file.save(name = str(profile.id)+'_genotype.raw',
                    content = ContentFile(genotype_data))
        return genotype
