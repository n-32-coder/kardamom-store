import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product

for p in Product.objects.filter(slug__contains='powder').order_by('id'):
    print(p.id, p.slug, 'active=' + str(p.is_active))
