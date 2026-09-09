"""Gateway helpers. Work with real Razorpay/Stripe keys; degrade cleanly without them."""
import hashlib
import hmac

import requests
from django.conf import settings

PLACEHOLDERS = {'', 'placeholder', 'rzp_test_placeholder', 'pk_test_placeholder', 'sk_test_placeholder'}


def _is_real(value):
    return bool(value) and 'placeholder' not in str(value).lower()


def razorpay_configured():
    return _is_real(settings.RAZORPAY_KEY_ID) and _is_real(settings.RAZORPAY_KEY_SECRET)


def stripe_configured():
    return _is_real(settings.STRIPE_SECRET_KEY) and _is_real(settings.STRIPE_PUBLIC_KEY)


def create_razorpay_order(amount_paise, receipt):
    """Create a Razorpay order via REST. Returns dict with id or raises RuntimeError."""
    resp = requests.post(
        'https://api.razorpay.com/v1/orders',
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET),
        json={'amount': amount_paise, 'currency': 'INR', 'receipt': receipt},
        timeout=15,
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(f'Razorpay error {resp.status_code}: {resp.text[:200]}')
    return resp.json()


def verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, signature):
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f'{razorpay_order_id}|{razorpay_payment_id}'.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def create_stripe_intent(amount_paise):
    """Create a Stripe PaymentIntent via REST. Returns dict with id/client_secret."""
    resp = requests.post(
        'https://api.stripe.com/v1/payment_intents',
        auth=(settings.STRIPE_SECRET_KEY, ''),
        data={'amount': amount_paise, 'currency': 'inr', 'automatic_payment_methods[enabled]': 'true'},
        timeout=15,
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(f'Stripe error {resp.status_code}: {resp.text[:200]}')
    return resp.json()
