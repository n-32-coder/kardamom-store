from django.db import models
from django.urls import reverse


class ProductCategory(models.Model):
    """Categories for cardamom products."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products_category'
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/products/?category={self.slug}"


class Product(models.Model):
    """Cardamom products in the store."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    pack_size_choices = [
        ('100g', '100 g'),
        ('250g', '250 g'),
        ('500g', '500 g'),
        ('1kg', '1 kg'),
    ]
    pack_size = models.CharField(max_length=10, choices=pack_size_choices, default='100g')
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    image = models.FileField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sku = models.CharField(max_length=50, unique=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products_product'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']
        indexes = [
            models.Index(fields=['-is_featured', 'name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.pack_size})"

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.id, self.slug])

    @property
    def discounted_price(self):
        """Calculate price with any discounts from metadata."""
        discount = self.metadata.get('discount', 0) if self.metadata else 0
        if discount:
            return round(self.price * (1 - discount / 100), 2)
        return self.price


class ProductReview(models.Model):
    """Customer reviews and ratings for products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products_product_review'
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'
        ordering = ['-created_at']
        unique_together = ['product', 'customer']

    def __str__(self):
        return f"{self.customer.username} - {self.rating}★"


class ProductImage(models.Model):
    """Multiple images per product."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to='products/images/')
    alt_text = models.CharField(max_length=200, blank=True)
    display_order = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'products_product_image'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['display_order', 'is_primary']

    def __str__(self):
        return f"Image for {self.product.name}"


class WishlistItem(models.Model):
    """Save-for-later favourites."""
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.CASCADE, related_name='wishlist_items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products_wishlistitem'
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        ordering = ['-created_at']
        unique_together = ['customer', 'product']

    def __str__(self):
        return f"{self.customer.username} ♥ {self.product.name}"