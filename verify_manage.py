"""Verify staff product management: add, edit, stock, delete."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from products.models import Product, ProductCategory

c = Client()
assert c.login(username='admin', password=os.environ.get('KARDAMOM_ADMIN_PASSWORD', 'Kardamom#3527631a'))

r = c.get('/products/manage/')
assert r.status_code == 200, 'manage list broken'
print('manage list: 200 OK')

cat = ProductCategory.objects.first()
r = c.post('/products/manage/add/', {
    'name': 'Test Pod', 'slug': '', 'category': cat.id,
    'description': 'QA pod', 'price': '100', 'stock': '5',
    'pack_size': '100g', 'sku': 'QA-TEST-100',
})
assert r.status_code == 302, 'product create broken'
p = Product.objects.get(sku='QA-TEST-100')
assert p.slug == 'test-pod', f'auto-slug broken: {p.slug}'
print(f'created {p.name} (slug auto: {p.slug}): OK')

r = c.post(f'/products/manage/{p.id}/edit/', {
    'name': 'Test Pod', 'slug': 'test-pod', 'category': cat.id,
    'description': 'QA pod', 'price': '150', 'stock': '42',
    'pack_size': '100g', 'sku': 'QA-TEST-100',
})
p.refresh_from_db()
assert r.status_code == 302 and str(p.price) == '150.00' and p.stock == 42
print('edit price + stock: OK')

r = c.get(f'/products/manage/{p.id}/delete/')
assert r.status_code == 200, 'delete confirm broken'
r = c.post(f'/products/manage/{p.id}/delete/')
assert r.status_code == 302 and not Product.objects.filter(sku='QA-TEST-100').exists()
print('delete: OK')

c.logout()
assert c.get('/products/manage/').status_code in (302, 403), 'not staff-guarded'
print('staff-only guard: OK')
print('MANAGE OK')
