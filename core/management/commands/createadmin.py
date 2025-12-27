from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create admin user if it does not exist'

    def handle(self, *args, **options):
        User = get_user_model()

        username = 'halosaasadmin'
        email = 'admin@halosaas.com'
        password = 'ChangeMe123!'

        # Check if admin exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Admin user "{username}" already exists'))
            return

        # Create admin
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" created with password: {password}'))
        self.stdout.write(self.style.ERROR('⚠️ CHANGE PASSWORD IMMEDIATELY AFTER LOGIN!'))