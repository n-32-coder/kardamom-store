import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from customers.models import Customer

u, created = Customer.objects.get_or_create(
    username='demo',
    defaults={'email': 'demo@kardamom.store', 'phone': '9876543210'},
)
u.set_password('demo123')
u.is_active = True
u.save()
print('demo user ready' if not created else 'demo user created')

c = Client()
assert c.login(username='demo', password='demo123'), 'demo login failed'
r = c.get('/')
assert 'Cart' in r.content.decode() and 'Dashboard' not in r.content.decode()
print('demo login works, sees shop nav: OK')
