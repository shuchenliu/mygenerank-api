from django.core.management.base import BaseCommand, CommandError

from generank.api import tasks


class Command(BaseCommand):
    help = 'Sends a registration email to a given user.'

    def add_arguments(self, parser):
        parser.add_argument('email_address', type=str)
        parser.add_argument('-c', '--code',  type=str, default='123456')
        parser.add_argument('-u', '--url', type=str,
            default='http://localhost:8000/test_register')

    def handle(self, *args, **options):
        email_address = options['email_address']
        code = options['code']
        url = options['url']
        tasks.send_registration_email_to_user(url, code, email_address)
        self.stdout.write(self.style.SUCCESS(
            'Email sent to %s' % email_address))
