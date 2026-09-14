"""Rebuild catalogue to the real grade/pack structure. Idempotent."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product, ProductCategory

PACKS = ['100g', '250g', '500g', '1kg']

# 1. Categories: rename bold -> Green Cardamom, add Seeds.
green_cat, _ = ProductCategory.objects.get_or_create(
    slug='green',
    defaults={'name': 'Green Cardamom', 'description': 'Graded green cardamom pods, 6mm to 7.5mm.'},
)
try:
    old_bold = ProductCategory.objects.get(slug='bold')
    for p in old_bold.products.all():
        p.category = green_cat
        p.save(update_fields=['category'])
    old_bold.delete()
    print('migrated old Bold category into Green Cardamom')
except ProductCategory.DoesNotExist:
    pass

premium_cat = ProductCategory.objects.get(slug='premium-green')
premium_cat.description = 'Super Bold 8mm & above, the top grade.'
premium_cat.save(update_fields=['description'])
powder_cat = ProductCategory.objects.get(slug='powder')
seeds_cat, _ = ProductCategory.objects.get_or_create(
    slug='seeds',
    defaults={'name': 'Cardamom Seeds', 'description': 'Decorticated cardamom seeds.'},
)

PRICE = {
    # (base per-pack prices)
    ('premium-green', '8mm+'): {'100g': 620, '250g': 1450, '500g': 2800, '1kg': 5400},
    ('green', '7.5mm'): {'100g': 540, '250g': 1280, '500g': 2480, '1kg': 4800},
    ('green', '7mm'): {'100g': 430, '250g': 980, '500g': 1890, '1kg': 3650},
    ('green', '6.5mm'): {'100g': 360, '250g': 840, '500g': 1620, '1kg': 3100},
    ('green', '6mm'): {'100g': 300, '250g': 710, '500g': 1370, '1kg': 2650},
}
GRADES = {
    ('premium-green', '8mm+'): ('Super Bold (8mm+)', 8.0, 'Premium Green Cardamom 8mm+'),
    ('green', '7.5mm'): ('7.5mm Bold', 7.5, 'Green Cardamom 7.5mm'),
    ('green', '7mm'): ('7mm Bold', 7.0, 'Green Cardamom 7mm'),
    ('green', '6.5mm'): ('6.5mm', 6.5, 'Green Cardamom 6.5mm'),
    ('green', '6mm'): ('6mm', 6.0, 'Green Cardamom 6mm'),
}
CATS = {'premium-green': premium_cat, 'green': green_cat}

made = 0
for (cat_slug, gkey), prices in PRICE.items():
    grade, size, base = GRADES[(cat_slug, gkey)]
    for pack in PACKS:
        slug = f"{cat_slug}-{gkey.replace('.', '_').replace('+', '')}-{pack}"
        _, created = Product.objects.get_or_create(
            slug=slug,
            defaults={
                'name': f'{base} {pack}', 'category': CATS[cat_slug],
                'grade': grade, 'size_mm': size, 'price': prices[pack],
                'stock': 50, 'pack_size': pack,
                'sku': f"KARD-{cat_slug[:4].upper()}-{gkey.replace('.', '')}-{pack.upper()}",
                'description': f'{base}, {grade} grade, {pack} pack.',
                'is_featured': (cat_slug, pack) == ('premium-green', '250g'),
            },
        )
        made += created

# Powder 250g + 500g.
for pack, price in [('250g', 990), ('500g', 1900)]:
    _, created = Product.objects.get_or_create(
        slug=f'powder-{pack}',
        defaults={'name': f'Cardamom Powder {pack}', 'category': powder_cat,
                  'grade': 'Fine Ground', 'price': price, 'stock': 60,
                  'pack_size': pack, 'sku': f'KARD-POWD-{pack.upper()}',
                  'description': f'Freshly ground cardamom powder, {pack}.'},
    )
    made += created
Product.objects.filter(slug='powder-100').update(grade='Fine Ground')

# Seeds 100g / 250g / 500g.
for pack, price in [('100g', 380), ('250g', 890), ('500g', 1720)]:
    _, created = Product.objects.get_or_create(
        slug=f'seeds-{pack}',
        defaults={'name': f'Cardamom Seeds {pack}', 'category': seeds_cat,
                  'grade': 'Bold Seeds', 'price': price, 'stock': 60,
                  'pack_size': pack, 'sku': f'KARD-SEED-{pack.upper()}',
                  'description': f'Decorticated cardamom seeds, {pack}.'},
    )
    made += created

# Tidy legacy names into the new scheme.
Product.objects.filter(slug='premium-green-8mm').update(
    name='Premium Green Cardamom 8mm+ 250g', grade='Super Bold (8mm+)', size_mm=8.0)
if Product.objects.filter(slug='green-7mm-250g').exists():
    # Canonical 7mm 250g already built above: drop the legacy seed row
    # instead of renaming it into a duplicate slug.
    Product.objects.filter(slug='bold-7mm').delete()
else:
    Product.objects.filter(slug='bold-7mm').update(
        slug='green-7mm-250g', name='Green Cardamom 7mm 250g',
        grade='7mm Bold', size_mm=7.0)

# Gift pack canonical name + photo (idempotent; replaces rename_gift.py).
Product.objects.filter(category__slug='gifts').update(
    name='Gift Pack', image='products/gift-pack.png')

# Legacy premium 250g is superseded by the new scheme: hide it from the store
# but keep it for existing orders' history. (green-7mm-250g was merged already.)
Product.objects.filter(slug__in=['premium-green-8mm']).update(is_active=False)

print(f'new products: {made}')
print(f"categories: {list(ProductCategory.objects.values_list('slug', flat=True))}")
print(f"total products: {Product.objects.count()}")
print('CATALOGUE OK')
