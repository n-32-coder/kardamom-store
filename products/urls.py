from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/review/', views.review_add, name='review_add'),
    path('products/<int:product_id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('wishlist/', views.wishlist_list, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('api/search/', views.api_product_search, name='api_search'),
    path('healthz/', views.healthz, name='healthz'),
]
