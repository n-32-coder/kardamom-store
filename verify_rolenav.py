import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

c = Client()
assert c.login(username='admin@kardamom.store', password=os.environ.get('KARDAMOM_ADMIN_PASSWORD', 'Kardamom#3527631a'))

r = c.get('/')
html = r.content.decode()
for hidden in ['/cart/', '/wishlist/', 'My Orders']:
    assert hidden not in html, f'admin nav leaks customer link: {hidden}'
for shown in ['Dashboard', 'Manage', 'Categories', 'Customers', 'Reviews']:
    assert shown in html, f'admin nav missing: {shown}'
print('admin sees workspace nav only: OK')

c.logout()
print('ROLE NAV OK')
