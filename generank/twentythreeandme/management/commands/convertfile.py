from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from generank.twentythreeandme import tasks
from generank.twentythreeandme.models import User, Profile, Genotype


class Command(BaseCommand):
    help = 'Begins the process of converting a user\'s data for CAD calculations.'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=str)
        parser.add_argument('profile_id', type=str)

    def handle(self, *args, **options):
        user_id = options['user_id']
        profile_id = options['profile_id']

        try:
            user = User.objects.get(api_user_id=user_id)
        except ObjectDoesNotExist as e:
            self.stdout.write(self.style.ERROR('No such user. %s' % e))
            return

        try:
            profile = Profile.objects.get(user=user, profile_id=profile_id)
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR('No such profile for user.'))
            return

        try:
            genotype = profile.genotype
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR('User has no genotypes.'))
            return

        if not genotype.genotype_file:
            self.stdout.write(self.style.ERROR('File does not exist.'))
            return

        tasks._convert_genotype.delay(str(genotype.id))
        self.stdout.write(self.style.SUCCESS('Tasks dispatched'))
