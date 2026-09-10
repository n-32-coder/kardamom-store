import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from products.models import Product

p = Product.objects.get(slug='powder-100')
p.image = 'products/powder.png'
p.is_active = True
p.save(update_fields=['image', 'is_active'])
print(f'image -> {p.image} on {p.name}')

c = Client()
r = c.get('/products/')
html = r.content.decode()
assert r.status_code == 200 and 'powder.png' in html
print('listing shows photo: OK')
r = c.get(p.get_absolute_url())
assert r.status_code == 200 and 'powder' in r.content.decode()
print('detail shows photo: OK')
print('POWDER PHOTO OK')
