from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates the admin user halosaasadmin with password ChangeMe123! if it does not exist.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'halosaasadmin'
        password = 'ChangeMe123!'
        email = 'halosaasadmin@example.com'
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Admin user '{username}' already exists."))
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Admin user '{username}' created with password: {password}"))
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates the admin user halosaasadmin with password ChangeMe123! if it does not exist.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'halosaasadmin'
        password = 'ChangeMe123!'
        email = 'halosaasadmin@example.com'
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Admin user '{username}' already exists."))
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Admin user '{username}' created with password: {password}"))from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates the admin user halosaasadmin with password ChangeMe123! if it does not exist.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'halosaasadmin'
        password = 'ChangeMe123!'
        email = 'halosaasadmin@example.com'
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Admin user '{username}' already exists."))
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Admin user '{username}' created with password: {password}"))