from django.db import models


class Category(models.Model):
    name  = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

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
    image    = models.ImageField(upload_to='plant_images/', null=True, blank=True)
    price    = models.PositiveIntegerField(default=0, verbose_name='Giá (VNĐ)')
    girth    = models.CharField(max_length=50, null=True, blank=True, verbose_name='Hoành gốc')
    height   = models.CharField(max_length=50, null=True, blank=True, verbose_name='Chiều cao')
    diameter = models.CharField(max_length=50, null=True, blank=True, verbose_name='Đường kính')
    stock    = models.PositiveIntegerField(default=10, verbose_name='Tồn kho')

    class Meta:
        verbose_name        = 'Cây'
        verbose_name_plural = 'Cây'
        ordering            = ['name']

    def __str__(self):
        return self.name

    @property
    def formatted_price(self):
        return f"{self.price:,}".replace(',', '.') + " VNĐ"

    @property
    def is_available(self):
        return self.stock > 0


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
    # ── Đã xóa hoàn toàn STATUS_CHOICES và trường status ──
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
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    plant    = models.ForeignKey(Plant, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price    = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity}× {self.plant.name if self.plant else '[đã xoá]'}"

    @property
    def subtotal(self):
        return self.price * self.quantity