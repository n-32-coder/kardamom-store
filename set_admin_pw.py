"""Set a strong admin password and print it once."""
import os
import secrets

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

pw = 'Kardamom#' + secrets.token_hex(4)
admin = get_user_model().objects.get(username='admin')
admin.set_password(pw)
admin.save()
print(f'NEW_ADMIN_PASSWORD={pw}')
