"""Verify gateway behaviour without real keys: graceful errors + signature check."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from orders.models import Order
from orders.payments import razorpay_configured, stripe_configured, verify_razorpay_signature
from products.models import Product

print('razorpay_configured:', razorpay_configured())
print('stripe_configured:', stripe_configured())
assert not razorpay_configured() and not stripe_configured()

c = Client()
assert c.login(username='admin@kardamom.store', password=os.environ.get('KARDAMOM_ADMIN_PASSWORD', 'Kardamom#3527631a'))
p = Product.objects.filter(is_active=True, stock__gt=2).first()
c.get(f'/cart/add/{p.id}/?quantity=1')

r = c.post('/orders/checkout/', {
    'address': 'X', 'phone': '9999999999', 'payment_method': 'razorpay',
})
assert r.status_code == 200 and b'keys are not set' in r.content, 'gateway guard broken'
print('razorpay-without-keys blocked with message: OK')
c.get('/cart/')  # cart kept

# Fake signature must be rejected.
assert verify_razorpay_signature('order_x', 'pay_y', 'bogus') is False
print('tampered signature rejected: OK')

# Pending gateway order + success callback path (simulate configured intent id).
from django.contrib.auth import get_user_model
user = get_user_model().objects.get(username='admin')
order = Order.objects.create(customer=user, total=100, address='X', phone='9',
                             payment_method='stripe', payment_id='pi_demo')
from orders.models import OrderItem
OrderItem.objects.create(order=order, product=p, quantity=1, price=p.price)
r = c.post('/orders/pay/success/', {'order_id': order.id, 'stripe_demo': '1'})
order.refresh_from_db()
assert r.status_code == 302 and order.status == 'confirmed', 'success callback broken'
print('payment success callback confirms order: OK')
print('PAY VERIFY OK')
