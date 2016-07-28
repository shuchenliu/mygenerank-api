from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from api.models import User, APNSDevice


class Command(BaseCommand):
    help = 'Sends a registration email to a given user.'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=str)

    def handle(self, *args, **options):
        user_id = options['user_id']

        try:
            user = User.object.get(id=user_id)
            device = APNSDevice.objects.get(user=user)
        except ObjectDoesNotExist:
            self.stdout.write(self.style.FAILURE('Could not send notification.'))
        devices.send_message('This is a test notification.')
        self.stdout.write(self.style.SUCCESS(
            'Notification sent sent to %s' % id))
