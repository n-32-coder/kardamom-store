"""Seed KARDAMOM with demo categories, products and admin user."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

from products.models import Product, ProductCategory

User = get_user_model()

admin, created = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@kardamom.store', 'is_staff': True, 'is_superuser': True},
)
if created:
    admin.set_password('admin123')
    admin.save()
    print('created admin / admin123')
else:
    print('admin exists')

cats = {}
for name, slug, desc in [
    ('Premium Green Cardamom', 'premium-green', 'Top-grade green cardamom pods.'),
    ('Bold Cardamom', 'bold', 'Extra-bold pods for rich flavour.'),
    ('Cardamom Powder', 'powder', 'Freshly ground cardamom powder.'),
    ('Gift Packs', 'gifts', 'Curated gift packs.'),
]:
    cat, _ = ProductCategory.objects.get_or_create(slug=slug, defaults={'name': name, 'description': desc})
    cats[slug] = cat
print(f'categories: {ProductCategory.objects.count()}')

items = [
    ('Premium Green Cardamom 8mm', 'premium-green-8mm', 1450, '250g', 'premium-green', True, 40, 'KARD-PREM-250'),
    ('Bold Cardamom 7mm', 'bold-7mm', 980, '250g', 'bold', False, 60, 'KARD-BOLD-250'),
    ('Cardamom Powder', 'powder-100', 420, '100g', 'powder', True, 100, 'KARD-POWD-100'),
    ('Festive Gift Pack', 'gift-festive', 1999, '500g', 'gifts', True, 25, 'KARD-GIFT-500'),
]
for name, slug, price, pack, cat_slug, featured, stock, sku in items:
    Product.objects.get_or_create(
        slug=slug,
        defaults={
            'name': name, 'price': price, 'pack_size': pack,
            'category': cats[cat_slug], 'is_featured': featured,
            'stock': stock, 'sku': sku,
            'description': f'{name} — premium quality from the finest plantations.',
        },
    )
print(f'products: {Product.objects.count()}')
print('SEED OK')
