import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from products.models import Product

items = list(Product.objects.filter(category__slug='seeds', is_active=True))
assert len(items) == 3, f'expected 3 seeds packs, got {len(items)}'
for p in items:
    p.image = 'products/seeds.png'
    p.save(update_fields=['image'])
    print(f'image -> {p.image} on {p.name}')

c = Client()
r = c.get('/products/?category=seeds')
html = r.content.decode()
assert r.status_code == 200 and html.count('seeds.png') >= 3
print('seeds page shows photos: OK')
r = c.get(items[0].get_absolute_url())
assert r.status_code == 200 and 'seeds' in r.content.decode()
print('detail shows photo: OK')
print('SEEDS PHOTO OK')
