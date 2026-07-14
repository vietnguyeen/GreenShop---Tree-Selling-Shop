from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('kho-cay/', views.kho_cay, name='kho_cay'),
    
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:plant_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:plant_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('dich-vu/', views.service_booking, name='service_booking'),
    path('dich-vu/thanh-cong/', views.service_success, name='service_success'),
]