"""Verify the real catalogue: grades, packs, pages."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from products.models import Product, ProductCategory

cats = {}
for c in ProductCategory.objects.all():
    cats[c.slug] = c.products.filter(is_active=True).count()
print('per-category counts (active):', cats)
assert cats.get('premium-green') == 4, 'premium needs 4 packs'
assert cats.get('green') == 16, 'green needs 4 grades x 4 packs'
assert cats.get('powder') == 3, 'powder needs 3 packs'
assert cats.get('seeds') == 3, 'seeds needs 3 packs'

p = Product.objects.get(slug='green-7mm-250g')
assert p.grade == '7mm Bold' and str(p.size_mm) == '7.0'
print(f'sample: {p.name} | {p.grade} | {p.size_mm}mm | Rs.{p.price}')

c = Client()
for url in ['/', '/products/', '/products/?category=green', '/products/?pack_size=1kg',
            '/products/?q=6.5mm', p.get_absolute_url()]:
    r = c.get(url)
    assert r.status_code == 200, f'{url} -> {r.status_code}'
    print(f'{url} -> 200')
print('CATALOGUE PAGES OK')
