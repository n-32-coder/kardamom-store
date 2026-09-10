"""Verify customer-side additions: timeline, move-to-cart, cancel, suggestions."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from cart.models import CartItem
from orders.models import Order
from products.models import Product, WishlistItem

c = Client()
assert c.login(username='demo', password='demo123'), 'demo login failed'

# Tracking timeline on own order (create one first).
p = Product.objects.filter(stock__gt=2).first()
c.get(f'/cart/add/{p.id}/?quantity=1')
c.post('/orders/checkout/', {'address': 'X', 'phone': '9', 'payment_method': 'cod'})
order = Order.objects.filter(customer__username='demo').latest('id')
r = c.get(f'/orders/{order.id}/')
html = r.content.decode()
assert r.status_code == 200 and 'Tracking' in html and 'Shipped' in html
print(f'timeline on order #{order.id}: OK')

# Cancel own pending order.
r = c.post(f'/orders/{order.id}/', {'action': 'cancel'})
order.refresh_from_db()
assert r.status_code == 302 and order.status == 'cancelled'
print('customer cancel pending: OK')
r = c.post(f'/orders/{order.id}/', {'action': 'cancel'})
assert r.status_code == 302  # already cancelled: message + redirect, still fine

# Wishlist -> move to cart.
WishlistItem.objects.get_or_create(customer=order.customer, product=p)
r = c.get(f'/wishlist/move/{p.id}/')
assert r.status_code == 302
assert CartItem.objects.filter(cart__customer=order.customer, product=p).exists()
assert not WishlistItem.objects.filter(customer=order.customer, product=p).exists()
print('move to cart: OK')

# Suggestions API wired + referenced by the listing page.
r = c.get('/api/search/?q=gree')
assert r.status_code == 200 and 'results' in r.json()
r = c.get('/products/')
assert 'productSearch' in r.content.decode() and 'searchHints' in r.content.decode()
print('suggestions API + live hints: OK')
print('CUSTOMER ADDITIONS OK')
