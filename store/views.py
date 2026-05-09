from django.shortcuts         import render, redirect, get_object_or_404
from django.contrib           import messages
from django.db                import transaction
from django.db.models         import F, Q
from django.core.mail         import EmailMultiAlternatives
from django.template.loader   import render_to_string
from django.utils.html        import strip_tags
from django.conf              import settings

from .models import Category, Plant, PruningRequest, Order, OrderItem


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
    """
    Helper dùng chung: gửi email HTML + text fallback.
    Dùng EmailMultiAlternatives để client mail cũ vẫn đọc được bản text thuần.
    Lỗi email không được làm crash luồng chính → dùng try/except + fail_silently.
    """
    try:
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(
            subject  = subject,
            body     = text_content,           # bản text thuần (fallback)
            from_email = settings.EMAIL_HOST_USER,
            to       = [settings.EMAIL_HOST_USER],
        )
        msg.attach_alternative(html_content, "text/html")  # bản HTML đẹp
        msg.send(fail_silently=False)
    except Exception as exc:
        # Log lỗi ra console, KHÔNG raise để không hỏng luồng nghiệp vụ
        print(f"[GreenShop] ⚠️  Lỗi gửi email: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# TRANG CHỦ
# ─────────────────────────────────────────────────────────────────────────────

def index(request):
    categories = Category.objects.all()
    plants     = Plant.objects.select_related('category').all()[:6]
    return render(request, 'store/index.html', {
        'categories':      categories,
        'plants':          plants,
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
# SET PHONE  (giữ lại để URL không 404)
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
# GIỎ HÀNG
# ─────────────────────────────────────────────────────────────────────────────

def add_to_cart(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id)

    if not plant.is_available:
        messages.error(request, f'"{plant.name}" hiện đã hết hàng.')
        return redirect(request.META.get('HTTP_REFERER', 'kho_cay'))

    cart = _get_cart(request)
    key  = str(plant_id)

    if key in cart:
        if cart[key]['quantity'] < plant.stock:
            cart[key]['quantity'] += 1
        else:
            messages.warning(
                request,
                f'"{plant.name}" đã đạt giới hạn tồn kho ({plant.stock}).'
            )
    else:
        cart[key] = {
            'price':    plant.price,
            'quantity': 1,
            'name':     plant.name,
        }

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
        subtotal = item['price'] * item['quantity']
        total   += subtotal
        cart_items.append({
            'plant':    plant,
            'quantity': item['quantity'],
            'price':    item['price'],
            'subtotal': subtotal,
        })

    return render(request, 'store/cart_detail.html', {
        'cart_items':      cart_items,
        'total_price':     total,
        'cart_item_count': len(cart_items),
    })


def update_cart(request, plant_id, action):
    cart = _get_cart(request)
    key  = str(plant_id)

    if key in cart:
        if action == 'increase':
            plant = get_object_or_404(Plant, id=plant_id)
            if cart[key]['quantity'] < plant.stock:
                cart[key]['quantity'] += 1
        elif action == 'decrease':
            cart[key]['quantity'] -= 1
            if cart[key]['quantity'] <= 0:
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

    # ── Lấy & lưu ngầm thông tin khách vào session ───────────────────────
    customer_name = request.POST.get('name',    '').strip()
    phone_number  = request.POST.get('phone',   '').strip()
    address       = request.POST.get('address', '').strip()

    request.session['customer_name']    = customer_name
    request.session['phone_number']     = phone_number
    request.session['customer_address'] = address
    request.session.modified = True

    # ── Tạo Order ─────────────────────────────────────────────────────────
    order = Order.objects.create(
        customer_name = customer_name,
        phone_number  = phone_number,
        address       = address,
        total_amount  = 0,
    )

    total      = 0
    items_data = []   # dữ liệu truyền vào template email

    for plant_id_str, item in cart.items():
        plant = get_object_or_404(Plant, id=int(plant_id_str))
        qty   = item['quantity']
        price = item['price']

        OrderItem.objects.create(
            order=order, plant=plant, quantity=qty, price=price,
        )

        # Trừ stock – thread-safe bằng F expression
        Plant.objects.filter(id=plant.id).update(stock=F('stock') - qty)
        Plant.objects.filter(id=plant.id, stock__lt=0).update(stock=0)

        subtotal    = price * qty
        total      += subtotal
        items_data.append({
            'plant':      plant,
            'quantity':   qty,
            'price':      price,
            'total_item': subtotal,
        })

    order.total_amount = total
    order.save()

    # ── Gửi email hóa đơn ─────────────────────────────────────────────────
    # Render template HTML thành chuỗi, truyền đầy đủ context
    html_content = render_to_string('store/email_bill.html', {
        'order': order,
        'items': items_data,
    })
    _send_html_email(
        subject      = f'🔔 ĐƠN HÀNG MỚI #{order.id} – {order.customer_name}',
        html_content = html_content,
        to_email     = settings.EMAIL_HOST_USER,
    )

    # ── Xóa giỏ hàng ─────────────────────────────────────────────────────
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
# CẮT TỈA
# ─────────────────────────────────────────────────────────────────────────────

def pruning_request_view(request):
    if request.method != 'POST':
        return redirect('home')

    name         = request.POST.get('name',         '').strip()
    phone_number = request.POST.get('phone_number', '').strip()
    message      = request.POST.get('message',      '').strip()

    # ── Lưu DB ────────────────────────────────────────────────────────────
    PruningRequest.objects.create(
        name         = name,
        phone_number = phone_number,
        message      = message,
    )

    # ── Gửi email thông báo nhanh cho chủ shop ────────────────────────────
    # Dùng f-string HTML inline vì nội dung đơn giản, không cần file template riêng
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head><meta charset="UTF-8"></head>
    <body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px;margin:0;">
      <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:12px;
                  overflow:hidden;border:1px solid #e0e0e0;">

        <div style="background:#1a3a24;padding:24px 28px;text-align:center;">
          <h2 style="color:#c8a84b;margin:0;font-family:Georgia,serif;font-size:1.3rem;">
            🌿 GREENSHOP – YÊU CẦU CẮT TỈA MỚI
          </h2>
        </div>

        <div style="padding:28px;">
          <p style="font-size:0.78rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.15em;color:#4a8c62;margin:0 0 10px;">
            Thông Tin Khách Hàng
          </p>
          <div style="background:#f5ede0;border-radius:8px;padding:16px 18px;">
            <table style="width:100%;font-size:0.9rem;border-collapse:collapse;">
              <tr>
                <td style="font-weight:700;color:#1a3a24;width:110px;padding:5px 0;">Họ tên:</td>
                <td style="color:#333;padding:5px 0;">{name}</td>
              </tr>
              <tr>
                <td style="font-weight:700;color:#1a3a24;padding:5px 0;">SĐT:</td>
                <td style="color:#333;padding:5px 0;">
                  <a href="tel:{phone_number}"
                     style="color:#d4863a;font-weight:700;text-decoration:none;">
                    {phone_number}
                  </a>
                </td>
              </tr>
              <tr>
                <td style="font-weight:700;color:#1a3a24;padding:5px 0;vertical-align:top;">
                  Yêu cầu:
                </td>
                <td style="color:#333;padding:5px 0;line-height:1.6;">
                  {message if message else '<em style="color:#999;">Không có ghi chú</em>'}
                </td>
              </tr>
            </table>
          </div>

          <p style="margin-top:20px;font-size:0.85rem;color:#666;line-height:1.7;">
            ⏰ Vui lòng gọi lại cho khách trong thời gian sớm nhất để xác nhận lịch.
          </p>
        </div>

        <div style="border-top:1px solid #eee;padding:16px 28px;
                    text-align:center;font-size:0.78rem;color:#999;">
          Email tự động từ hệ thống <strong>GreenShop</strong>.
        </div>
      </div>
    </body>
    </html>
    """

    _send_html_email(
        subject      = f'✂️ YÊU CẦU CẮT TỈA MỚI – {name} ({phone_number})',
        html_content = html_content,
        to_email     = settings.EMAIL_HOST_USER,
    )

    messages.success(request, 'Đã gửi yêu cầu cắt tỉa! Chúng tôi sẽ liên hệ sớm.')
    return redirect('home')