from django.urls import path

from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('pay/<int:order_id>/', views.pay_order, name='pay_order'),
    path('pay/success/', views.payment_success, name='payment_success'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('', views.order_list, name='order_list'),
]
