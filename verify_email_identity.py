import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from customers.models import Customer

# Same display name twice must be allowed.
Customer.objects.filter(email__in=['qa1@x.com', 'qa2@x.com']).delete()
a = Customer.objects.create_user(username='SameName', email='qa1@x.com', password='Xx#11111')
b = Customer.objects.create_user(username='SameName', email='qa2@x.com', password='Xx#22222')
print('duplicate display names allowed: OK')

# Same email twice must be rejected.
from django.db import IntegrityError
try:
    Customer.objects.create_user(username='Other', email='qa1@x.com', password='Xx#33333')
    raise SystemExit('duplicate email ALLOWED - broken!')
except IntegrityError:
    print('duplicate email rejected: OK')

# Login works with email.
c = Client()
assert c.login(username='qa1@x.com', password='Xx#11111'), 'email login failed'
print('email login: OK')
r = c.get('/')
assert 'SameName' in r.content.decode()
print('display name shown: OK')

Customer.objects.filter(email__in=['qa1@x.com', 'qa2@x.com']).delete()
print('EMAIL IDENTITY OK')
