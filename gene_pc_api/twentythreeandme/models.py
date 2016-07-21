import uuid

from django.conf import settings
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
#import logging


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.CharField(max_length=100, blank=True, editable = False,
                                unique = True)
    profile_id = models.CharField(max_length=100, blank=True, editable = False)
    token = models.CharField(max_length=100, blank=True,
                                 verbose_name = 'Bearer Token')
    email = models.EmailField(blank=True, editable = False)

    ## API user properties
    apiuserid = models.UUIDField(blank=True, editable=False, null = True)

    resource_url = 'https://api.23andme.com/1/demo/user/'
    def __str__(self):
        return '<TwentyThreeAndMe: User: %s>' % self.email

    @staticmethod
    def from_json(data, token):
        uobj = User()
        uobj.user_id = data['id']
        uobj.email = data['email']
        uobj.token = token

        return uobj


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE,
         blank=True, null=True)
    profile_id = models.CharField(max_length=100)
    genotyped = models.BooleanField(blank=True)

    resource_url = 'https://api.23andme.com/1/demo/user/{}/'

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

    resource_url = 'https://api.23andme.com/1/demo/genomes/{profile_id}/'

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
                    content = ContentFile(genotype_data) )
        return genotype
