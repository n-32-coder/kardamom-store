"""Verify KARDAMOM pages render."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from products.models import Product

c = Client()
checks = [
    ('home', '/'),
    ('product_list', '/products/'),
    ('register', '/accounts/register/'),
    ('login', '/accounts/login/'),
    ('cart_requires_login', '/cart/'),
]
for name, url in checks:
    r = c.get(url)
    print(f'{name}: {url} -> {r.status_code}')

p = Product.objects.first()
if p:
    r = c.get(p.get_absolute_url())
    print(f'product_detail: {p.get_absolute_url()} -> {r.status_code}')
    r = c.get('/api/search/?q=cardamom')
    print(f'api_search: /api/search/?q=cardamom -> {r.status_code} {r.content[:80]!r}')
print('VERIFY DONE')
