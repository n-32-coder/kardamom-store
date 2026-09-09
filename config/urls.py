"""KARDAMOM Premium Cardamom Store URL Configuration."""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('customers.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('', include('products.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'KARDAMOM Store Admin'
admin.site.site_title = 'KARDAMOM Admin'
admin.site.index_title = 'Welcome to KARDAMOM Administration'
