from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import Cart
from products.models import Product
from .models import Order, OrderItem
from .payments import (
    create_razorpay_order,
    create_stripe_intent,
    razorpay_configured,
    stripe_configured,
    verify_razorpay_signature,
)


def _build_order(user, address, phone, payment_method, items, total):
    order = Order.objects.create(
        customer=user, total=total, address=address,
        phone=phone, payment_method=payment_method,
    )
    for item in items:
        OrderItem.objects.create(
            order=order, product=item.product,
            quantity=item.quantity, price=item.price_at_addition,
        )
    return order


def _finalize_order(order):
    """Confirm order: decrement stock, mark confirmed, notify."""
    for item in order.items.select_related('product'):
        if item.product.stock >= item.quantity:
            item.product.stock -= item.quantity
            item.product.save(update_fields=['stock'])
    order.status = 'confirmed'
    order.save(update_fields=['status'])
    Cart.objects.filter(customer=order.customer).delete()
    if order.customer.email:
        send_mail(
            f'KARDAMOM order #{order.id} confirmed',
            f'Thank you! Your order of Rs. {order.total} is {order.status}.',
            None, [order.customer.email], fail_silently=True,
        )


@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(customer=request.user)
    items = list(cart.items.select_related('product'))
    if not items:
        messages.info(request, 'Your cart is empty.')
        return redirect('product_list')
    total = cart.get_total_price()

    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()
        payment_method = request.POST.get('payment_method', 'cod')
        if not address or not phone:
            messages.error(request, 'Address and phone are required.')
            return render(request, 'orders/checkout.html', {'items': items, 'total': total})

        if payment_method == 'razorpay' and not razorpay_configured():
            messages.error(request, 'Razorpay keys are not set — choose COD/UPI or add live keys.')
            return render(request, 'orders/checkout.html', {'items': items, 'total': total})
        if payment_method == 'stripe' and not stripe_configured():
            messages.error(request, 'Stripe keys are not set — choose COD/UPI or add live keys.')
            return render(request, 'orders/checkout.html', {'items': items, 'total': total})

        if payment_method in ('cod', 'upi'):
            order = _build_order(request.user, address, phone, payment_method, items, total)
            _finalize_order(order)
            messages.success(request, f'Order #{order.id} placed successfully!')
            return redirect('order_detail', order_id=order.id)

        # Online payment: create pending order, hand off to gateway.
        order = _build_order(request.user, address, phone, payment_method, items, total)
        return redirect('pay_order', order_id=order.id)

    return render(request, 'orders/checkout.html', {'items': items, 'total': total})


@login_required
def pay_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user, status='pending')
    amount_paise = int(order.total * 100)

    if order.payment_method == 'razorpay':
        try:
            gw = create_razorpay_order(amount_paise, receipt=f'kardamom-{order.id}')
        except RuntimeError as e:
            messages.error(request, str(e))
            return redirect('order_detail', order_id=order.id)
        order.payment_id = gw['id']
        order.save(update_fields=['payment_id'])
        return render(request, 'orders/pay.html', {
            'order': order, 'gateway': 'razorpay',
            'key_id': settings.RAZORPAY_KEY_ID,
            'gateway_order_id': gw['id'], 'amount_paise': amount_paise,
        })

    if order.payment_method == 'stripe':
        try:
            intent = create_stripe_intent(amount_paise)
        except RuntimeError as e:
            messages.error(request, str(e))
            return redirect('order_detail', order_id=order.id)
        order.payment_id = intent['id']
        order.save(update_fields=['payment_id'])
        return render(request, 'orders/pay.html', {
            'order': order, 'gateway': 'stripe',
            'key_id': settings.STRIPE_PUBLIC_KEY,
            'client_secret': intent.get('client_secret', ''),
        })

    return redirect('order_detail', order_id=order.id)


@login_required
def payment_success(request):
    order_id = request.POST.get('order_id') or request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id, customer=request.user, status='pending')

    if order.payment_method == 'razorpay':
        sig = request.POST.get('razorpay_signature', '')
        if not verify_razorpay_signature(
            request.POST.get('razorpay_order_id', ''),
            request.POST.get('razorpay_payment_id', ''), sig,
        ):
            messages.error(request, 'Payment verification failed.')
            return redirect('order_detail', order_id=order.id)
        order.payment_id = request.POST.get('razorpay_payment_id', order.payment_id)

    order.save(update_fields=['payment_id'])
    _finalize_order(order)
    messages.success(request, f'Payment received — order #{order.id} confirmed!')
    return redirect('order_detail', order_id=order.id)


@login_required
def order_list(request):
    if request.user.is_staff:
        if request.method == 'POST':
            order = get_object_or_404(Order, id=request.POST.get('order_id'))
            new_status = request.POST.get('status')
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save(update_fields=['status'])
                messages.success(request, f'Order #{order.id} → {order.get_status_display()}.')
            return redirect('order_list')
        return render(request, 'orders/staff_list.html', {
            'orders': Order.objects.select_related('customer').all(),
            'status_choices': Order.STATUS_CHOICES,
        })
    return render(request, 'orders/list.html', {
        'orders': request.user.orders.all(),
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'orders/detail.html', {'order': order})


@staff_member_required
def dashboard(request):
    from datetime import timedelta

    from django.db.models.functions import TruncDate
    from django.utils import timezone

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'status':
            order = get_object_or_404(Order, id=request.POST.get('order_id'))
            new_status = request.POST.get('status')
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save(update_fields=['status'])
                messages.success(request, f'Order #{order.id} → {order.get_status_display()}.')
        elif action == 'restock':
            product = get_object_or_404(Product, id=request.POST.get('product_id'))
            try:
                qty = max(1, int(request.POST.get('qty', 0)))
            except ValueError:
                qty = 0
            if qty:
                product.stock += qty
                product.save(update_fields=['stock'])
                messages.success(request, f'{product.name} restocked +{qty}.')
        return redirect('dashboard')

    stats = Order.objects.aggregate(revenue=Sum('total'), count=Count('id'))
    by_status = list(
        Order.objects.values('status').annotate(count=Count('id'), revenue=Sum('total'))
    )
    week_ago = timezone.now() - timedelta(days=6)
    trend = list(
        Order.objects.filter(created_at__gte=week_ago)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(revenue=Sum('total'), count=Count('id'))
        .order_by('day')
    )
    low_stock = list(Product.objects.filter(stock__lt=10).order_by('stock')[:10])
    top_products = list(
        OrderItem.objects.values('product__name')
        .annotate(qty=Sum('quantity'), revenue=Sum('price'))
        .order_by('-qty')[:5]
    )
    recent_orders = list(Order.objects.select_related('customer')[:10])
    from customers.models import Customer
    return render(request, 'orders/dashboard.html', {
        'revenue': stats['revenue'] or 0,
        'order_count': stats['count'] or 0,
        'product_count': Product.objects.count(),
        'customer_count': Customer.objects.count(),
        'by_status': by_status,
        'trend': trend,
        'low_stock': low_stock,
        'low_count': Product.objects.filter(stock__lt=10).count(),
        'top_products': top_products,
        'recent_orders': recent_orders,
        'status_choices': Order.STATUS_CHOICES,
    })
