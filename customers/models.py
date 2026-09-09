from django.db import models
from django.contrib.auth.models import AbstractUser


class Customer(AbstractUser):
    """Custom user model for KARDAMOM premium store."""
    PHONE_MAX_LENGTH = 20
    
    phone = models.CharField(max_length=PHONE_MAX_LENGTH, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.FileField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    referred_by = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers_customer'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['-created_at']

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def display_name(self):
        if self.profile_image:
            return self.username
        return self.full_name or self.username

    # Fix related_name clashes with Django's default User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customer_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customer_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )