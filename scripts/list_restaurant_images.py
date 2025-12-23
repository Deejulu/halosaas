import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')
django.setup()

from restaurants.models import Restaurant

def main():
    qs = Restaurant.objects.all()
    print('id | name | slug | logo | banner_image')
    for r in qs:
        print(r.id, '|', r.name, '|', r.slug, '|', getattr(r.logo, 'name', None), '|', getattr(r.banner_image, 'name', None))

if __name__ == '__main__':
    main()
