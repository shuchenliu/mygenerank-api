from django.core.management.base import BaseCommand, CommandError

from api import tasks


class Command(BaseCommand):
    help = 'Kicks off tasks to import the data for a given user from 23andMe.'

    def add_arguments(self, parser):
        parser.add_argument('user_id', nargs=1, type=str)
        parser.add_argument('profile_id', nargs=1, type=str)
        parser.add_argument('token', nargs=1, type=str)

    def handle(self, *args, **options):
        user_id = options['user_id']
        profile_id = options['profile_id']
        token = options['token']

        tasks.twentythreeandme_delayed_import_task(token, user_id, profile_id)
        self.stdout.write(self.style.SUCCESS('Tasks dispatched'))
