from django.core.management.base import BaseCommand, CommandError

from generank.twentythreeandme import tasks


class Command(BaseCommand):
    help = 'Kicks off tasks to import the data for a given user from 23andMe.'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=str)
        parser.add_argument('profile_id', type=str)
        parser.add_argument('token', type=str)
        parser.add_argument('run_after', type=bool)

    def handle(self, *args, **options):
        user_id = options['user_id']
        profile_id = options['profile_id']
        token = options['token']
        run_after = options['run_after']

        tasks.twentythreeandme.import_account.delay(
            token, user_id, profile_id, run_after=run_after)
        self.stdout.write(self.style.SUCCESS('Tasks dispatched'))
