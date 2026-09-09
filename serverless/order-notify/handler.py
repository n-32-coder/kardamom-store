"""Order-notify serverless function: reacts to order events, sends notifications.

Runs on Knative Serving (scale-to-zero, event-driven). Trigger it with a
CloudEvent like: {"order_id": 12, "email": "a@b.com", "total": "980.00"}.
"""
import json
import os


def handler(event, context=None):
    """CloudEvent entrypoint (also callable directly for local testing)."""
    data = event if isinstance(event, dict) else json.loads(event)
    order_id = data.get('order_id')
    email = data.get('email', 'unknown')
    total = data.get('total', '0')
    line = f'[order-notify] order #{order_id} ({total}) -> notify {email}'
    print(line)
    # Production: plug in SES/SendGrid here using env credentials.
    return {'ok': True, 'order_id': order_id, 'notified': email}


if __name__ == '__main__':
    import sys

    print(handler(json.loads(sys.argv[1] if len(sys.argv) > 1 else '{}')))
