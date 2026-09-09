from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product
from .models import Cart, CartItem


@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(customer=request.user)
    items = cart.items.select_related('product')
    return render(request, 'cart/detail.html', {
        'cart': cart,
        'items': items,
        'total': cart.get_total_price(),
    })


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    try:
        quantity = max(1, int(request.GET.get('quantity', 1)))
    except ValueError:
        quantity = 1
    cart, _ = Cart.objects.get_or_create(customer=request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={'quantity': quantity, 'price_at_addition': product.price},
    )
    if not created:
        item.quantity += quantity
        item.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_item_count': cart.items.count(),
            'item_total': item.subtotal,
        })
    messages.success(request, f'{product.name} added to cart.')
    return redirect('product_detail', product_id=product.id, slug=product.slug)


@login_required
def cart_remove(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    name = item.product.name
    cart = item.cart
    item.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_item_count': cart.items.count()})
    messages.success(request, f'{name} removed from cart.')
    return redirect('cart_detail')
