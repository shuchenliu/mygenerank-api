from django.core.management.base import BaseCommand, CommandError

from generank.api import tasks
from generank.celery import app


class Command(BaseCommand):
    help = 'Tell all (or specific) workers to stop consuming from ``queue``.'

    def add_arguments(self, parser):
        parser.add_argument('queue', type=str)
        parser.add_argument('-d', '--destination',  type=str, default=None)

    def handle(self, *args, **options):
        queue = options['queue']
        destination = options['destination']

        if destination:
            app.control.cancel_consumer(queue, destination=destination)
            self.stdout.write(self.style.SUCCESS(
                'Consumer cancelled for queue %s on %s' % (queue, destination)))
        else:
            app.control.cancel_consumer(queue)
            self.stdout.write(self.style.SUCCESS(
                'All consumers cancelled for queue %s' % queue))
