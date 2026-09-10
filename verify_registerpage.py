import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client

from customers.models import Customer

c = Client()
r = c.get('/accounts/register/')
html = r.content.decode()
assert r.status_code == 200 and 'auth-card' in html and 'Join the store' in html
print('classy register renders: OK')

Customer.objects.filter(username='qareg').delete()
r = c.post('/accounts/register/', {
    'username': 'qareg', 'email': 'qa@x.com', 'phone': '9000000001',
    'password1': 'Strong#pass9', 'password2': 'Strong#pass9',
})
assert r.status_code == 302 and Customer.objects.filter(username='qareg').exists()
print('registration works: OK')
Customer.objects.filter(username='qareg').delete()
print('REGISTER PAGE OK')
