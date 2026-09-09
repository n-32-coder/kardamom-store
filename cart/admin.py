from django.contrib import admin
from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin interface for Cart."""
    list_display = ['customer', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin interface for CartItem."""
    list_display = ['cart', 'product', 'quantity', 'price_at_addition']
    list_filter = ['cart', 'product']
    raw_id_fields = ('cart', 'product')
    list_editable = ['quantity']
