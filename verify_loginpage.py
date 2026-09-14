import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

c = Client()
r = c.get('/accounts/login/')
html = r.content.decode()
assert r.status_code == 200 and 'auth-card' in html and 'Welcome back' in html
print('classy login renders: OK')
assert c.login(username='demo@kardamom.store', password='demo123')
print('login still works: OK')
r = c.get('/accounts/profile/')
assert r.status_code == 200
print('LOGIN PAGE OK')
