from django.shortcuts         import render, redirect, get_object_or_404
from django.contrib           import messages
from django.db                import transaction
from django.db.models         import Q
from django.core.mail         import EmailMultiAlternatives
from django.template.loader   import render_to_string
from django.utils.html        import strip_tags
from django.conf              import settings

from .forms                   import ServiceOrderForm
from .models                  import Category, Plant, PruningRequest, Order, OrderItem, ServiceOrder


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _get_cart(request):
    return request.session.get('cart', {})

def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def _cart_item_count(request):
    return sum(item['quantity'] for item in _get_cart(request).values())

def _send_html_email(subject, html_content, to_email):
    try:
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(
            subject  = subject,
            body     = text_content,
            from_email = settings.EMAIL_HOST_USER,
            to       = [settings.EMAIL_HOST_USER],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
    except Exception as exc:
        print(f"[Hoa Kiểng Hoàng Nam] ⚠️  Lỗi gửi email: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# TRANG CHỦ
# ─────────────────────────────────────────────────────────────────────────────

def index(request):
    # Lấy toàn bộ cây đang có hàng (is_available=True) cho Slider
    all_plants = Plant.objects.select_related('category').filter(is_available=True)
    
    # Lấy 10 cây mới nhất chưa bán để hiển thị
    featured_plants = Plant.objects.select_related('category').filter(is_available=True).order_by('-id')[:10]
    
    return render(request, 'store/index.html', {
        'all_plants':      all_plants,
        'featured_plants': featured_plants,
        'cart_item_count': _cart_item_count(request),
    })


# ─────────────────────────────────────────────────────────────────────────────
# KHO CÂY
# ─────────────────────────────────────────────────────────────────────────────

def kho_cay(request):
    query  = request.GET.get('q', '').strip()
    plants = Plant.objects.select_related('category').all()

    if query:
        plants = plants.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query)
        )

    return render(request, 'store/kho_cay.html', {
        'plants':          plants,
        'query':           query,
        'categories':      Category.objects.all(),
        'cart_item_count': _cart_item_count(request),
    })


# ─────────────────────────────────────────────────────────────────────────────
# SET PHONE
# ─────────────────────────────────────────────────────────────────────────────

def set_phone(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number', '').strip()
        if phone:
            request.session['phone_number'] = phone
            request.session.modified = True
        return redirect(request.POST.get('next', '/'))
    return redirect('home')


# ─────────────────────────────────────────────────────────────────────────────
# GIỎ HÀNG (Logic Độc Bản)
# ─────────────────────────────────────────────────────────────────────────────

def add_to_cart(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id)

    # Chặn nếu cây đã có chủ
    if not plant.is_available:
        messages.error(request, f'Rất tiếc, "{plant.name}" hiện đã có chủ.')
        return redirect(request.META.get('HTTP_REFERER', 'kho_cay'))

    cart = _get_cart(request)
    key  = str(plant_id)

    # Nếu cây đã nằm trong giỏ thì không tăng số lượng, chỉ báo lỗi nhẹ
    if key in cart:
        messages.warning(request, f'"{plant.name}" đã nằm trong giỏ hàng của bạn rồi (sản phẩm độc bản).')
    else:
        cart[key] = {
            'price':    plant.price,
            'quantity': 1,
            'name':     plant.name,
        }
        messages.success(request, f'Đã thêm "{plant.name}" vào giỏ hàng!')

    _save_cart(request, cart)
    return redirect('cart_detail')


def cart_detail(request):
    raw_cart   = _get_cart(request)
    cart_items = []
    total      = 0

    for plant_id_str, item in raw_cart.items():
        try:
            plant = Plant.objects.get(id=int(plant_id_str))
        except Plant.DoesNotExist:
            continue
            
        subtotal = item['price'] * 1 # Ép số lượng = 1
        total   += subtotal
        cart_items.append({
            'plant':    plant,
            'quantity': 1,
            'price':    item['price'],
            'subtotal': subtotal,
        })

    return render(request, 'store/cart_detail.html', {
        'cart_items':      cart_items,
        'total_price':     total,
        'cart_item_count': len(cart_items),
    })


def update_cart(request, plant_id, action):
    # Với hàng độc bản, nút tăng/giảm đã bị gỡ.
    # Hàm này chủ yếu dùng để dự phòng nếu khách gọi xóa sản phẩm
    cart = _get_cart(request)
    key  = str(plant_id)

    if key in cart:
        if action == 'decrease':
            del cart[key]

    _save_cart(request, cart)
    return redirect('cart_detail')


def remove_from_cart(request, plant_id):
    cart = _get_cart(request)
    cart.pop(str(plant_id), None)
    _save_cart(request, cart)
    return redirect('cart_detail')


# ─────────────────────────────────────────────────────────────────────────────
# CHECKOUT
# ─────────────────────────────────────────────────────────────────────────────

@transaction.atomic
def checkout(request):
    if request.method != 'POST':
        return redirect('cart_detail')

    cart = _get_cart(request)
    if not cart:
        messages.error(request, 'Giỏ hàng đang trống.')
        return redirect('cart_detail')

    customer_name = request.POST.get('name',    '').strip()
    phone_number  = request.POST.get('phone',   '').strip()
    address       = request.POST.get('address', '').strip()

    request.session['customer_name']    = customer_name
    request.session['phone_number']     = phone_number
    request.session['customer_address'] = address
    request.session.modified = True

    order = Order.objects.create(
        customer_name = customer_name,
        phone_number  = phone_number,
        address       = address,
        total_amount  = 0,
    )

    total      = 0
    items_data = []

    for plant_id_str, item in cart.items():
        plant = get_object_or_404(Plant, id=int(plant_id_str))
        qty   = 1 # Ép số lượng = 1
        price = item['price']

        # Chặn nếu cây vừa bị người khác mua trước đó vài giây
        if not plant.is_available:
            messages.error(request, f'Xin lỗi, cây "{plant.name}" vừa được khách khác đặt mua. Vui lòng chọn cây khác!')
            return redirect('cart_detail')

        OrderItem.objects.create(order=order, plant=plant, quantity=qty, price=price)

        # Chuyển trạng thái cây thành ĐÃ BÁN (is_available = False)
        Plant.objects.filter(id=plant.id).update(is_available=False)

        subtotal = price * qty
        total   += subtotal
        items_data.append({
            'plant':      plant,
            'quantity':   qty,
            'price':      price,
            'total_item': subtotal,
        })

    order.total_amount = total
    order.save()

    html_content = render_to_string('store/email_bill.html', {
        'order': order,
        'items': items_data,
    })
    _send_html_email(
        subject      = f'🔔 ĐƠN HÀNG MỚI #{order.id} – {order.customer_name}',
        html_content = html_content,
        to_email     = settings.EMAIL_HOST_USER,
    )

    if 'cart' in request.session:
        del request.session['cart']
    request.session.modified = True

    return redirect('order_success', order_id=order.id)


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_success.html', {
        'order':           order,
        'cart_item_count': _cart_item_count(request),
    })


# ─────────────────────────────────────────────────────────────────────────────
# DỊCH VỤ CẢNH QUAN
# ─────────────────────────────────────────────────────────────────────────────

def service_booking(request):
    if request.method == 'POST':
        form = ServiceOrderForm(request.POST)

        if form.is_valid():
            service_order = form.save()
            service_label = service_order.get_service_type_display()
            
            html_content = render_to_string('store/email_service.html', {
                'service_order': service_order,
            })

            _send_html_email(
                subject      = (
                    f'🌿 DỊCH VỤ MỚI [{service_label}] – '
                    f'{service_order.customer_name} ({service_order.phone_number})'
                ),
                html_content = html_content,
                to_email     = settings.EMAIL_HOST_USER,
            )

            messages.success(
                request,
                'Đã gửi yêu cầu dịch vụ! Chúng tôi sẽ liên hệ xác nhận sớm nhất.'
            )
            return redirect('service_success')

        return render(request, 'store/service_booking.html', {
            'form':            form,
            'cart_item_count': _cart_item_count(request),
        })

    form = ServiceOrderForm()
    return render(request, 'store/service_booking.html', {
        'form':            form,
        'cart_item_count': _cart_item_count(request),
    })


def service_success(request):
    return render(request, 'store/service_success.html', {
        'cart_item_count': _cart_item_count(request),
    })