"""End-to-end verify: wishlist, review, checkout, orders, dashboard."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from products.models import Product

c = Client()
assert c.login(username='admin@kardamom.store', password=os.environ.get('KARDAMOM_ADMIN_PASSWORD', 'Kardamom#3527631a')), 'login failed'

p = Product.objects.filter(is_active=True, stock__gt=2).first()
print(f'using product: {p.name}')

r = c.get('/cart/add/%d/?quantity=1' % p.id)
print('cart_add:', r.status_code)

r = c.get('/wishlist/toggle/%d/' % p.id)
print('wishlist_toggle:', r.status_code)
r = c.get('/wishlist/')
assert r.status_code == 200 and p.name in r.content.decode(), 'wishlist page broken'
print('wishlist page: 200 OK')

r = c.post('/products/%d/review/' % p.id, {'rating': '5', 'comment': 'Excellent quality!'})
print('review_add:', r.status_code)
r = c.get(p.get_absolute_url())
assert 'Excellent quality!' in r.content.decode(), 'review not shown'
print('review shown on detail: OK')

r = c.get('/orders/checkout/')
print('checkout page:', r.status_code)
r = c.post('/orders/checkout/', {
    'address': '123 Spice Street, Kochi', 'phone': '9876543210', 'payment_method': 'cod',
})
print('place order:', r.status_code, getattr(r, 'url', ''))
assert r.status_code == 302, 'order not created'

r = c.get('/orders/')
assert r.status_code == 200 and 'Order #' in r.content.decode(), 'order list broken'
print('order list: 200 OK')

from orders.models import Order
order = Order.objects.filter(customer__username='admin').latest('id')
r = c.get(f'/orders/{order.id}/')
assert r.status_code == 200, 'order detail broken'
print(f'order detail #{order.id}: 200 OK, total Rs. {order.total}')

r = c.get('/orders/dashboard/')
assert r.status_code == 200, 'dashboard broken'
print('dashboard (revenue/status/low-stock/top): 200 OK')

r = c.get('/cart/')
assert 'empty' in r.content.decode().lower(), 'cart not cleared after order'
print('cart cleared after checkout: OK')
print('FULL FLOW OK')
