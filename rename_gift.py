import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product

p = Product.objects.filter(category__slug='gifts').first()
assert p is not None, 'no gift product found'
p.name = 'Gift Pack'
p.image = 'products/gift-pack.png'
p.save(update_fields=['name', 'image'])
print(f'renamed -> {p.name}, image -> {p.image}')
print('GIFT OK')
