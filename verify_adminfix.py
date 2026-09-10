"""Verify the three admin-side fixes."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from orders.models import Order
from products.models import Product

c = Client()
pw = os.environ.get('KARDAMOM_ADMIN_PASSWORD', 'Kardamom#3527631a')
assert c.login(username='admin', password=pw)

# 1. Staff can open any order detail (was 404).
order = Order.objects.exclude(customer__username='admin').first() or Order.objects.first()
r = c.get(f'/orders/{order.id}/')
assert r.status_code == 200, 'staff order detail still 404'
print(f'staff opens order #{order.id}: OK')

# 2. Stock steppers on manage list.
p = Product.objects.filter(is_active=True).order_by('stock').first()
before = p.stock
r = c.post('/products/manage/', {'action': 'stock', 'product_id': p.id, 'delta': '10'})
p.refresh_from_db()
assert r.status_code == 302 and p.stock == before + 10
r = c.post('/products/manage/', {'action': 'stock', 'product_id': p.id, 'delta': '-9999'})
p.refresh_from_db()
assert p.stock == before + 10, 'stock went negative!'
print(f'stock stepper +10 / floor guard: OK ({p.stock})')

# 3. Manage search + customer order filter.
r = c.get('/products/manage/?q=6.5mm')
assert r.status_code == 200 and '6.5mm' in r.content.decode()
print('manage search: OK')
r = c.get('/orders/?customer=admin')
assert r.status_code == 200 and 'Order #' in r.content.decode()
r = c.get('/orders/?customer=nobody-xyz')
assert r.status_code == 200 and 'Order #' not in r.content.decode()
print('customer order filter: OK')
print('ADMIN FIXES OK')
