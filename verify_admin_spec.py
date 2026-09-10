"""Verify the full admin spec: categories, grade/size, customers, all-orders, packed, reviews."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from orders.models import Order
from products.models import Product, ProductCategory, ProductReview

c = Client()
pw = os.environ.get('KARDAMOM_ADMIN_PASSWORD', 'Kardamom#3527631a')
assert c.login(username='admin', password=pw)

# Categories CRUD.
r = c.post('/categories/manage/add/', {'name': 'QA Category', 'slug': '', 'description': 'temp'})
assert r.status_code == 302, 'category create broken'
cat = ProductCategory.objects.get(slug='qa-category')
print('category create (auto-slug): OK')
r = c.post(f'/categories/manage/{cat.id}/edit/', {'name': 'QA Category', 'slug': 'qa-category', 'description': 'Seeds'})
assert r.status_code == 302, 'category edit broken'
r = c.post(f'/categories/manage/{cat.id}/delete/')
assert r.status_code == 302 and not ProductCategory.objects.filter(slug='qa-category').exists()
print('category edit + delete: OK')

# Product grade + size_mm.
p = Product.objects.first()
r = c.post(f'/products/manage/{p.id}/edit/', {
    'name': p.name, 'slug': p.slug, 'category': p.category_id, 'grade': 'Alleppey Green',
    'size_mm': '8.0', 'description': p.description, 'price': str(p.price),
    'stock': p.stock, 'pack_size': p.pack_size, 'sku': p.sku or 'QA-X',
})
p.refresh_from_db()
assert r.status_code == 302 and p.grade == 'Alleppey Green' and str(p.size_mm) == '8.0'
print(f'grade + size_mm saved ({p.grade}, {p.size_mm}mm): OK')

# Customers page.
r = c.get('/customers/manage/')
assert r.status_code == 200 and 'admin' in r.content.decode()
print('customers list: OK')

# Staff sees ALL orders; packed status exists.
r = c.get('/orders/')
assert r.status_code == 200 and 'Order #' in r.content.decode()
print('staff all-orders list: OK')
order = Order.objects.first()
r = c.post('/orders/dashboard/', {'action': 'status', 'order_id': order.id, 'status': 'packed'})
order.refresh_from_db()
assert order.status == 'packed', 'packed status broken'
print(f"order #{order.id} -> packed: OK")

# Reviews manage + remove.
review = ProductReview.objects.first()
assert review is not None, 'no review to test (post one first)'
r = c.get('/reviews/manage/')
assert r.status_code == 200 and review.comment[:20] in r.content.decode()
r = c.post(f'/reviews/manage/{review.id}/delete/')
assert r.status_code == 302 and not ProductReview.objects.filter(pk=review.pk).exists()
print('review remove: OK')

# Dashboard totals.
r = c.get('/orders/dashboard/')
html = r.content.decode()
assert 'Products / Customers' in html
print('dashboard totals: OK')
print('ADMIN SPEC OK')
