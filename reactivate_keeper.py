import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product

p = Product.objects.get(slug='green-7mm-250g')
p.is_active = True
p.save(update_fields=['is_active'])
print(f'reactivated #{p.id} {p.name}')
