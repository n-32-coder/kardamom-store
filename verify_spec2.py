"""Verify spec gaps: payment states, account toggle, month report, profile/password."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from orders.models import Order
from products.models import Product

c = Client()
pw = os.environ.get('KARDAMOM_ADMIN_PASSWORD', 'Kardamom#3527631a')
assert c.login(username='admin', password=pw)

# Payment states: COD -> pending, gateway success -> paid, staff override.
p = Product.objects.filter(is_active=True, stock__gt=2).first()
c.get(f'/cart/add/{p.id}/?quantity=1')
r = c.post('/orders/checkout/', {'address': 'X', 'phone': '9', 'payment_method': 'cod'})
order = Order.objects.latest('id')
assert order.payment_status == 'pending', order.payment_status
print(f'COD order #{order.id}: payment pending OK')
r = c.post('/orders/', {'order_id': order.id, 'status': order.status, 'payment_status': 'paid'})
order.refresh_from_db()
assert order.payment_status == 'paid'
print('staff payment override -> paid: OK')

# Account activate/deactivate (+ self-guard).
from customers.models import Customer
target = Customer.objects.exclude(pk=c.session['_auth_user_id'] if '_auth_user_id' in c.session else 0).first()
if target is None or target.pk == int(c.session.get('_auth_user_id', 0)):
    target = Customer.objects.filter(is_staff=False).first()
was = target.is_active
r = c.post('/customers/manage/', {'user_id': target.id})
target.refresh_from_db()
assert target.is_active != was
r = c.post('/customers/manage/', {'user_id': target.id})
target.refresh_from_db()
assert target.is_active == was
print(f'account toggle for {target.username}: OK')
me = Customer.objects.get(username='admin')
r = c.post('/customers/manage/', {'user_id': me.id})
me.refresh_from_db()
assert me.is_active, 'self-deactivation guard broken!'
print('self-deactivation blocked: OK')

# Month filter + CSV export.
r = c.get('/orders/dashboard/?month=2026-09')
assert r.status_code == 200
r = c.get('/orders/dashboard/?export=csv')
assert r.status_code == 200 and 'order,date,customer' in r.content.decode()
print('month filter + CSV export: OK')

# Profile edit + password change (as a normal customer).
c.logout()
c.login(username='admin', password=pw)
r = c.post('/accounts/profile/', {
    'first_name': 'Store', 'last_name': 'Admin', 'email': 'admin@kardamom.store',
    'phone': '9999999999', 'address': 'Kochi', 'date_of_birth': '',
})
assert r.status_code == 302
me.refresh_from_db()
assert me.phone == '9999999999', 'profile edit broken'
print('profile edit: OK')
r = c.post('/accounts/password/', {
    'old_password': pw, 'new_password1': 'Newpass#9999', 'new_password2': 'Newpass#9999',
})
assert r.status_code == 302, 'password change broken'
c.logout()
assert c.login(username='admin', password='Newpass#9999'), 'new password login failed'
me.set_password(pw)
me.save()
print('password change + login: OK')
print('SPEC GAPS OK')
