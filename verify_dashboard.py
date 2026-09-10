"""Verify the overview dashboard: stats, charts, manage links; status via orders page."""
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
assert 'Recent Orders' not in html, 'dashboard still lists orders'
for link in ['Manage', 'Categories', 'Customers', 'Reviews', 'Best-Selling']:
    assert link in html, f'dashboard missing: {link}'
print('overview dashboard (stats, charts, links): OK')

order = Order.objects.first()
r = c.post('/orders/', {'order_id': order.id, 'status': 'delivered'})
order.refresh_from_db()
assert r.status_code == 302 and order.status == 'delivered', 'orders-page status broken'
print(f'order #{order.id} -> delivered from orders page: OK')

p = Product.objects.filter(is_active=True).order_by('stock').first()
before = p.stock
r = c.post('/products/manage/', {'action': 'stock', 'product_id': p.id, 'delta': '25'})
p.refresh_from_db()
assert r.status_code == 302 and p.stock == before + 25, 'stepper broken'
print(f'{p.name} stepper {before} -> {p.stock}: OK')

c.logout()
r = c.get('/orders/dashboard/')
assert r.status_code in (302, 403), 'dashboard not staff-guarded'
print('staff-only guard: OK')
print('DASHBOARD OK')
