from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Plant, PruningRequest, Order, OrderItem, ServiceOrder


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'plant_count', 'preview_image']
    search_fields = ['name']

    @admin.display(description='Số cây')
    def plant_count(self, obj):
        return obj.plants.count()

    @admin.display(description='Ảnh')
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:6px"/>', obj.image.url)
        return '—'


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display   = ['name', 'category', 'formatted_price', 'stock', 'stock_status', 'preview_image']
    list_filter    = ['category']
    search_fields  = ['name', 'category__name']
    list_editable  = ['stock']
    ordering       = ['category', 'name']

    @admin.display(description='Giá')
    def formatted_price(self, obj):
        return obj.formatted_price

    @admin.display(description='Trạng thái kho')
    def stock_status(self, obj):
        if obj.stock <= 0:
            # Đã fix: Truyền chữ vào thông qua {}
            return format_html('<span style="color:#c0392b;font-weight:700">{}</span>', '● Hết hàng')
        if obj.stock <= 3:
            return format_html('<span style="color:#d4863a;font-weight:700">⚡ Sắp hết ({})</span>', obj.stock)
        # Đã fix: Truyền chữ vào thông qua {}
        return format_html('<span style="color:#2a5c3f;font-weight:700">{}</span>', '✓ Còn hàng')

    @admin.display(description='Ảnh')
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:6px"/>', obj.image.url)
        return '—'


class OrderItemInline(admin.TabularInline):
    model         = OrderItem
    extra         = 0
    readonly_fields = ['plant', 'quantity', 'price', 'subtotal']
    can_delete    = False

    @admin.display(description='Thành tiền')
    def subtotal(self, obj):
        return f"{obj.subtotal:,}".replace(',', '.') + " đ"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display   = ['id', 'customer_name', 'phone_number', 'formatted_total', 'created_at']
    list_filter    = [ 'created_at']
    search_fields  = ['customer_name', 'phone_number']
    readonly_fields = ['created_at', 'total_amount']
    inlines        = [OrderItemInline]
    ordering       = ['-created_at']

    @admin.display(description='Tổng tiền')
    def formatted_total(self, obj):
        return obj.formatted_total


@admin.register(PruningRequest)
class PruningRequestAdmin(admin.ModelAdmin):
    list_display  = ['name', 'phone_number', 'short_message', 'created_at']
    search_fields = ['name', 'phone_number']
    ordering      = ['-created_at']

    @admin.display(description='Ghi chú')
    def short_message(self, obj):
        return obj.message[:60] + '…' if len(obj.message) > 60 else obj.message
    
@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display  = ['customer_name', 'phone_number', 'service_type', 'grass_option', 'created_at']
    list_filter   = ['service_type']
    search_fields = ['customer_name', 'phone_number']
    ordering      = ['-created_at']