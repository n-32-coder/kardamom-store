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
    path('products/<int:product_id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('wishlist/', views.wishlist_list, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('api/search/', views.api_product_search, name='api_search'),
    path('healthz/', views.healthz, name='healthz'),
]
