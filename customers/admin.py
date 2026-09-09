from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin interface for Customer model."""
    list_display = ['username', 'email', 'phone', 'is_verified', 'date_joined']
    list_filter = ['is_verified', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'phone']
    readonly_fields = ['date_joined', 'updated_at']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'date_of_birth', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'updated_at')}),
    )
    filter_horizontal = ('groups', 'user_permissions')


# Custom admin site header
admin.site.site_header = 'KARDAMOM Premium Cardamom Store Admin'
admin.site.site_title = 'KARDAMOM Admin'
admin.site.index_title = 'Welcome to KARDOM Administration'
