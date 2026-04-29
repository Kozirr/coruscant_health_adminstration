from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Prints a Coruscant Health Official name from firstname and lastname arguments.'

    def add_arguments(self, parser):
        parser.add_argument('firstname', nargs='?', type=str, help='First name of the official')
        parser.add_argument('lastname', nargs='?', type=str, help='Last name of the official')

    def handle(self, *args, **options):
        firstname = options.get('firstname')
        lastname = options.get('lastname')

        if not firstname or not lastname:
            self.stderr.write(self.style.ERROR('Usage: python manage.py health_official <firstname> <lastname>'))
            return

        self.stdout.write(f'Coruscant Health Official: {firstname} {lastname}')
