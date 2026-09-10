from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/review/', views.review_add, name='review_add'),
    path('products/manage/', views.product_manage_list, name='product_manage_list'),
    path('products/manage/add/', views.product_manage_edit, name='product_create'),
    path('products/manage/<int:pk>/edit/', views.product_manage_edit, name='product_update'),
    path('products/manage/<int:pk>/delete/', views.product_manage_delete, name='product_delete'),
    path('categories/manage/', views.category_manage_list, name='category_manage_list'),
    path('categories/manage/add/', views.category_manage_edit, name='category_create'),
    path('categories/manage/<int:pk>/edit/', views.category_manage_edit, name='category_update'),
    path('categories/manage/<int:pk>/delete/', views.category_manage_delete, name='category_delete'),
    path('customers/manage/', views.customer_manage_list, name='customer_manage_list'),
    path('reviews/manage/', views.review_manage_list, name='review_manage_list'),
    path('reviews/manage/<int:pk>/delete/', views.review_manage_delete, name='review_delete'),
    path('products/<int:product_id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('wishlist/', views.wishlist_list, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('wishlist/move/<int:product_id>/', views.wishlist_move_to_cart, name='wishlist_move'),
    path('api/search/', views.api_product_search, name='api_search'),
    path('healthz/', views.healthz, name='healthz'),
]
