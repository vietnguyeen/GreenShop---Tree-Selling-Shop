from django.contrib import admin
from .models import Category, Plant, Order, OrderItem, ServiceOrder

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    list_editable = ('price', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('price',)
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'phone_number', 'total_amount', 'created_at')
    search_fields = ('customer_name', 'phone_number')
    inlines = [OrderItemInline]

@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'phone_number', 'service_type', 'created_at')
    list_filter = ('service_type', 'grass_option')
    search_fields = ('customer_name', 'phone_number')