#!/usr/bin/env python
import os
import sys
import django

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')

django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()


username = 'halosaasadmin'
email = 'halosaasadmin@example.com'
password = os.environ.get('ADMIN_PASSWORD', 'david0011')

if User.objects.filter(username=username).exists():
    print("✅ Admin user already exists")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print("✅ Admin user created successfully")
    print("⚠️ IMPORTANT: Log in and change password immediately!")
