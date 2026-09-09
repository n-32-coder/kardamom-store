"""Verify interactive staff dashboard: charts render, status + restock actions work."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from orders.models import Order
from products.models import Product

c = Client()
assert c.login(username='admin', password=os.environ.get('KARDAMOM_ADMIN_PASSWORD', 'Kardamom#3527631a'))

r = c.get('/orders/dashboard/')
assert r.status_code == 200, 'dashboard broken'
html = r.content.decode()
assert 'trendChart' in html and 'statusChart' in html, 'charts missing'
assert 'Recent Orders' in html, 'orders panel missing'
print('dashboard renders with charts: OK')

order = Order.objects.first()
r = c.post('/orders/dashboard/', {'action': 'status', 'order_id': order.id, 'status': 'shipped'})
order.refresh_from_db()
assert r.status_code == 302 and order.status == 'shipped', 'status update broken'
print(f'order #{order.id} -> shipped: OK')

p = Product.objects.order_by('stock').first()
before = p.stock
r = c.post('/orders/dashboard/', {'action': 'restock', 'product_id': p.id, 'qty': '25'})
p.refresh_from_db()
assert r.status_code == 302 and p.stock == before + 25, 'restock broken'
print(f'{p.name} restocked {before} -> {p.stock}: OK')

# Non-staff cannot see it.
c.logout()
r = c.get('/orders/dashboard/')
assert r.status_code in (302, 403), 'dashboard not staff-guarded'
print('staff-only guard: OK')
print('DASHBOARD OK')
