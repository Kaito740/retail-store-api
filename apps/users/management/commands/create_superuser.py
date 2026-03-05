from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser using environment variables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default=None,
            help='Username for superuser (default: from DJANGO_SUPERUSER_USERNAME env)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default=None,
            help='Email for superuser (default: from DJANGO_SUPERUSER_EMAIL env)',
        )
        parser.add_argument(
            '--password',
            type=str,
            default=None,
            help='Password for superuser (default: from DJANGO_SUPERUSER_PASSWORD env)',
        )

    def handle(self, *args, **options):
        import os

        username = options['username'] or os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = options['email'] or os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = options['password'] or os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username or not email or not password:
            self.stdout.write(
                self.style.ERROR(
                    'Missing required arguments. Provide --username, --email, --password '
                    'or set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, '
                    'DJANGO_SUPERUSER_PASSWORD environment variables.'
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser "{username}" already exists. Skipping creation.')
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(f'Superuser "{username}" created successfully!')
        )
