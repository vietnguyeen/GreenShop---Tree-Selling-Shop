from django.db import models


class Category(models.Model):
    name  = models.CharField(max_length=100, verbose_name='Tên danh mục')
    image = models.ImageField(
        upload_to='category_images/', null=True, blank=True, verbose_name='Ảnh'
    )

    class Meta:
        verbose_name        = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering            = ['name']

    def __str__(self):
        return self.name


class Plant(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='plants', verbose_name='Danh mục'
    )
    name     = models.CharField(max_length=200, verbose_name='Tên cây')
    image    = models.ImageField(
        upload_to='plant_images/', null=True, blank=True, verbose_name='Ảnh đại diện'
    )
    image2   = models.ImageField(
        upload_to='plant_images/', null=True, blank=True, verbose_name='Ảnh phụ 1'
    )
    image3 = models.ImageField(
        upload_to='plant_images/', null=True, blank=True, verbose_name="Ảnh phụ 2"
    )
    # Đã thêm dấu đóng ngoặc ) cho image4
    image4 = models.ImageField(
        upload_to='plant_images/', null=True, blank=True, verbose_name="Ảnh phụ 3"
    )
    price    = models.PositiveIntegerField(default=0,  verbose_name='Giá (VNĐ)')
    girth    = models.CharField(max_length=50,  null=True, blank=True, verbose_name='Hoành gốc')
    height   = models.CharField(max_length=50,  null=True, blank=True, verbose_name='Chiều cao')
    diameter = models.CharField(max_length=50,  null=True, blank=True, verbose_name='Đường kính tán')
    
    # Đã thay thế hoàn toàn 'stock' bằng 'is_available'
    is_available = models.BooleanField(default=True, verbose_name='Còn hàng / Sẵn sàng giao')

    class Meta:
        verbose_name        = 'Cây'
        verbose_name_plural = 'Cây'
        ordering            = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    @property
    def formatted_price(self):
        return f"{self.price:,}".replace(',', '.') + " VNĐ"


class PruningRequest(models.Model):
    name         = models.CharField(max_length=200, verbose_name='Tên khách')
    phone_number = models.CharField(max_length=20,  verbose_name='SĐT')
    message      = models.TextField(blank=True,     verbose_name='Ghi chú')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Yêu cầu cắt tỉa'
        verbose_name_plural = 'Yêu cầu cắt tỉa'
        ordering            = ['-created_at']

    def __str__(self):
        return f"Cắt tỉa – {self.name} ({self.phone_number})"


class Order(models.Model):
    customer_name = models.CharField(max_length=200, verbose_name='Tên khách')
    phone_number  = models.CharField(max_length=20,  verbose_name='SĐT')
    address       = models.TextField(verbose_name='Địa chỉ')
    total_amount  = models.PositiveIntegerField(default=0, verbose_name='Tổng tiền')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'
        ordering            = ['-created_at']

    def __str__(self):
        return f"#{self.id} – {self.customer_name}"

    @property
    def formatted_total(self):
        return f"{self.total_amount:,}".replace(',', '.') + " VNĐ"


class OrderItem(models.Model):
    order    = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items'
    )
    plant    = models.ForeignKey(Plant, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price    = models.PositiveIntegerField()   # snapshot giá tại thời điểm mua

    def __str__(self):
        name = self.plant.name if self.plant else '[đã xoá]'
        return f"{self.quantity}× {name}"

    @property
    def subtotal(self):
        return self.price * self.quantity


# ─────────────────────────────────────────────────────────────────────────────
# YÊU CẦU 2: Model Đặt Dịch Vụ Cảnh Quan
# ─────────────────────────────────────────────────────────────────────────────

class ServiceOrder(models.Model):

    SERVICE_CHOICES = [
        ('cat_tia',      'Cắt tỉa'),
        ('bao_duong',    'Bảo dưỡng'),
        ('lop_tham_co',  'Lợp thảm cỏ'),
    ]

    GRASS_CHOICES = [
        ('co_thai',     'Cỏ Thái'),
        ('co_la_gung',  'Cỏ Lá Gừng'),
    ]

    customer_name = models.CharField(max_length=200, verbose_name='Tên khách')
    phone_number  = models.CharField(max_length=20,  verbose_name='SĐT')
    address       = models.TextField(verbose_name='Địa chỉ')
    service_type  = models.CharField(
        max_length=20, choices=SERVICE_CHOICES, verbose_name='Loại dịch vụ'
    )
    grass_option  = models.CharField(
        max_length=20, choices=GRASS_CHOICES,
        null=True, blank=True,           # chỉ bắt buộc khi chọn lợp thảm cỏ
        verbose_name='Tùy chọn cỏ'
    )
    note          = models.TextField(blank=True, verbose_name='Ghi chú')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Đơn đặt dịch vụ'
        verbose_name_plural = 'Đơn đặt dịch vụ'
        ordering            = ['-created_at']

    def __str__(self):
        return (
            f"[{self.get_service_type_display()}] "
            f"{self.customer_name} – {self.phone_number}"
        )