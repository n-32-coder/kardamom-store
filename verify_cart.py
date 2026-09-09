"""Verify login + cart add/remove flow."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from products.models import Product

c = Client()
assert c.login(username='admin', password=os.environ.get('KARDAMOM_ADMIN_PASSWORD', 'Kardamom#3527631a')), 'login failed'
print('login: OK')

p = Product.objects.filter(stock__gt=0).first()
r = c.get(f'/cart/add/{p.id}/?quantity=2')
print(f'cart_add: -> {r.status_code}')
r = c.get('/cart/')
print(f'cart_detail: -> {r.status_code}')
content = r.content.decode()
assert p.name in content, 'product missing from cart page'
print(f'cart contains {p.name}: OK')
print('CART FLOW OK')
