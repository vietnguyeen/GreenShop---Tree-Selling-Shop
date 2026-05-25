from django.urls import path
from . import views

urlpatterns = [
    # Trang chủ & Kho cây
    path('', views.index, name='home'),
    path('kho-cay/', views.kho_cay, name='kho_cay'),
    
    # Giỏ hàng & Thanh toán
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:plant_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:plant_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:plant_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('dich-vu/', views.service_booking, name='service_booking'),
    path('dich-vu/thanh-cong/', views.service_success, name='service_success'),
    
    # Tiện ích
    path('set-phone/', views.set_phone, name='set_phone'),
]