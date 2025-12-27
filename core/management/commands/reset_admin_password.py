from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Resets the admin password for halosaasadmin to ChangeMe123! (one-time use, then delete)'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'halosaasadmin'
        new_password = 'ChangeMe123!'
        user = User.objects.filter(username=username).first()
        if user:
            user.set_password(new_password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Password for '{username}' has been reset to: {new_password}"))
            self.stdout.write(self.style.WARNING("Log in and change this password immediately!"))
        else:
            self.stdout.write(self.style.ERROR(f"User '{username}' not found."))from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Resets the admin password for halosaasadmin to ChangeMe123! (one-time use, then delete)'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'halosaasadmin'
        new_password = 'ChangeMe123!'
        user = User.objects.filter(username=username).first()
        if user:
            user.set_password(new_password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Password for '{username}' has been reset to: {new_password}"))
            self.stdout.write(self.style.WARNING("Log in and change this password immediately!"))
        else:
            self.stdout.write(self.style.ERROR(f"User '{username}' not found."))
