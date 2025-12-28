from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import Client

from restaurants.models import Restaurant

class Command(BaseCommand):
    help = 'Inspect restaurant dashboard HTML as a restaurant owner'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'tmp_owner_cmd'
        password = 'tmp_password'
        user, created = User.objects.get_or_create(username=username, defaults={'email':'tmp@example.com'})
        if created:
            user.set_password(password)
            user.role = 'restaurant_owner'
            user.save()
        else:
            user.role = 'restaurant_owner'
            user.set_password(password)
            user.save()

        Restaurant.objects.filter(owner=user).delete()
        rest, _ = Restaurant.objects.get_or_create(name='Temp Rest Cmd', owner=user, defaults={'slug':'temp-rest-cmd','description':'test','opening_time':'09:00:00','closing_time':'21:00:00','is_active':True})

        c = Client()
        logged = c.login(username=username, password=password)
        self.stdout.write('logged in: %s' % logged)
        resp = c.get('/restaurants/dashboard/')
        self.stdout.write('status_code: %s' % resp.status_code)
        content = resp.content.decode('utf-8')
        for i, line in enumerate(content.splitlines(), start=1):
            if 'Add Restaurant' in line or 'Add Your' in line or 'manage_restaurant' in line or 'fa-plus' in line:
                self.stdout.write('%s: %s' % (i, line.strip()))
        with open('tmp_owner_dashboard_cmd.html', 'w', encoding='utf-8') as f:
            f.write(content)
        self.stdout.write('Saved tmp_owner_dashboard_cmd.html')
