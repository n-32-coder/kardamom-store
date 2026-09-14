"""Merge the duplicate green-7mm-250g: keep the new-scheme product, move history onto it."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cart.models import CartItem
from orders.models import OrderItem
from products.models import Product, ProductImage, ProductReview, WishlistItem

dupes = list(Product.objects.filter(slug='green-7mm-250g').order_by('id'))
print('dupes:', [(p.id, p.name, p.is_active) for p in dupes])
assert len(dupes) == 2, 'expected exactly 2'
legacy = next(p for p in dupes if not p.is_active)
new = next(p for p in dupes if p.is_active)

moved = 0
for model, field in [(OrderItem, 'product'), (CartItem, 'product'),
                     (ProductReview, 'product'), (WishlistItem, 'product'),
                     (ProductImage, 'product')]:
    n = model.objects.filter(**{field: legacy}).update(**{field: new})
    moved += n
print(f'moved {moved} related rows onto #{new.id}')
legacy.delete()
print('legacy deleted; remaining:', Product.objects.filter(slug='green-7mm-250g').count())
print('MERGE OK')
