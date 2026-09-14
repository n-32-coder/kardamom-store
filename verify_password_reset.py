import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse

c = Client()

# GET the reset form
r = c.get('/accounts/password/reset/')
assert r.status_code == 200 and 'Reset your password' in r.content.decode()
print('reset form renders: OK')

# POST with an existing email (admin@kardamom.store)
r = c.post('/accounts/password/reset/', {'email': 'admin@kardamom.store'})
assert r.status_code == 302
print('reset request accepts existing email: OK')

# GET the done page
r = c.get('/accounts/password/reset/done/')
assert r.status_code == 200 and 'Check your inbox' in r.content.decode()
print('reset done page renders: OK')

print('PASSWORD RESET FLOW OK')
