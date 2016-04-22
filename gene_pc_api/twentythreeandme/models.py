import uuid

from django.db import models
from django.core.files.storage import FileSystemStorage


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=100)
    email = models.EmailField()

    resource_url = 'https://api.23andme.com/1/demo/user/{}/?email=true'

    def __str__(self):
        return '<TwentyThreeAndMe: User: %s>' % self.email

    def from_json(data):
        user = User()
        user.user_id = data['id']
        user.email = data['email']
        return user


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
        related_name='profiles', blank=True, null=True)
    profile_id = models.CharField(max_length=100)
    genotyped = models.BooleanField()

    resource_url = 'https://api.23andme.com/1/demo/user/{}/'

    @property
    def has_imported(self):
        """ Whether or not a given user has been imported. """
        return not self.profile_id and self.genome.genome_file_url

    def __str__(self):
        return '<TwentyThreeAndMe: Profile: %s>' % self.user.email

    def from_json(data):
        user_id = data['id']
        profiles = []
        for profile_data in data['profiles']:
            profile = Profile()
            profile.profile_id = profile_data['id']


            profile.user = User.objects.filter(user_id=user_id)[0]
            profiles.append(profile)
        return profiles

class Genome(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE,
        blank=True)

    fs = FileSystemStorage(location='/tmp/django_tmp/')
    genome_file = models.FileField(storage=fs)

    resource_url = 'https://api.23andme.com/1/demo/genome/{}/'

    @property
    def genome_file_url(self):
        return self.genome_file.url

    def __str__(self):
        return '<TwentyThreeAndMe: Genome: %s>' % self.profile.id
