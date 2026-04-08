from django.contrib import admin
from .models import Product, Order, OrderItem


# OrderItems ko Order ke andar dikhao
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image_emoji')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'total_amount', 'session_key', 'created_at')
    list_filter = ('status',)
    inlines = [OrderItemInline]
    readonly_fields = ('idempotency_key', 'stripe_session_id', 'created_at', 'updated_at')