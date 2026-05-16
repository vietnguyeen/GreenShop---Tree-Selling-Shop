from django.urls import path
from . import views

urlpatterns = [
    # ── Trang chính ──────────────────────────────────────────────────────────
    path('',                                    views.index,               name='home'),
    path('kho-cay/',                            views.kho_cay,             name='kho_cay'),

    # ── Lazy Registration ─────────────────────────────────────────────────────
    path('set-phone/',                          views.set_phone,           name='set_phone'),

    # ── Giỏ hàng ─────────────────────────────────────────────────────────────
    path('gio-hang/',                           views.cart_detail,         name='cart_detail'),
    path('them-vao-gio/<int:plant_id>/',        views.add_to_cart,         name='add_to_cart'),
    path('cap-nhat-gio/<int:plant_id>/<str:action>/',
                                                views.update_cart,         name='update_cart'),
    path('xoa-khoi-gio/<int:plant_id>/',        views.remove_from_cart,    name='remove_from_cart'),

    # ── Thanh toán ────────────────────────────────────────────────────────────
    path('thanh-toan/',                         views.checkout,            name='checkout'),
    path('dat-hang-thanh-cong/<int:order_id>/', views.order_success,       name='order_success'),

    # ── Cắt tỉa (legacy – giữ lại) ───────────────────────────────────────────
    path('cat-tia/',                            views.pruning_request_view, name='pruning_request'),

    # ── Dịch vụ cảnh quan (mới) ───────────────────────────────────────────────
    path('dich-vu/',                            views.service_booking,     name='service_booking'),
    path('dich-vu/cam-on/',                     views.service_success,     name='service_success'),
]