from django.contrib import admin
from .models import Product, ProductCategory, ProductImage, ProductReview, WishlistItem


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """Admin interface for ProductCategory."""
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product."""
    list_display = ['name', 'slug', 'price', 'pack_size', 'category', 'is_active', 'is_featured', 'sku']
    list_filter = ['is_active', 'is_featured', 'category', 'pack_size']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'price', 'sku')}),
        ('Inventory', {'fields': ('stock', 'pack_size', 'category')}),
        ('Media', {'fields': ('image',)}),
        ('Display', {'fields': ('is_active', 'is_featured')}),
        ('SEO & Metadata', {'fields': ('metadata',), 'classes': ('collapse',)}),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin interface for ProductImage."""
    list_display = ['product', 'display_order', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['product__name', 'alt_text']
    raw_id_fields = ('product',)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Admin interface for ProductReview."""
    list_display = ['product', 'customer', 'rating', 'verified_purchase', 'created_at']
    list_filter = ['verified_purchase', 'rating']
    search_fields = ['product__name', 'customer__username', 'title']
    raw_id_fields = ('product', 'customer')
    list_editable = ['verified_purchase']


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'created_at']
    raw_id_fields = ('customer', 'product')
