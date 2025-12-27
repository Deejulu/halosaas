import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'halosaasadmin'
new_password = 'ChangeMe123!'

user = User.objects.filter(username=username).first()
if user:
    user.set_password(new_password)
    user.save()
    print(f"✅ Password for '{username}' has been reset to: {new_password}")
    print("⚠️ IMPORTANT: Log in and change this password immediately!")
else:
    print(f"❌ User '{username}' not found.")
