import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from products.models import Product

p = Product.objects.get(category__slug='gifts')
print('name:', p.name)
print('image:', p.image)
assert p.name == 'Gift Pack'

c = Client()
r = c.get('/products/')
html = r.content.decode()
assert r.status_code == 200 and 'Gift Pack' in html and 'gift-pack.png' in html
print('listing shows photo: OK')
r = c.get(p.get_absolute_url())
assert r.status_code == 200 and 'gift-pack' in r.content.decode()
print('detail shows photo: OK')
print('GIFT PAGE OK')
