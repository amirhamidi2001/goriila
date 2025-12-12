from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'product_price', 'quantity', 'subtotal')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'user',
        'status',
        'total',
        'created_date'
    )
    list_filter = ('status', 'created_date')
    search_fields = (
        'order_number',
        'user__email',
        'shipping_full_name',
        'shipping_phone'
    )
    readonly_fields = (
        'order_number',
        'user',
        'subtotal',
        'shipping_cost',
        'tax',
        'total',
        'created_date',
        'updated_date'
    )
    
    fieldsets = (
        ('اطلاعات سفارش', {
            'fields': ('order_number', 'user', 'status', 'created_date', 'updated_date')
        }),
        ('آدرس ارسال', {
            'fields': (
                'shipping_full_name',
                'shipping_phone',
                'shipping_address_line1',
                'shipping_address_line2',
                'shipping_city',
                'shipping_state',
                'shipping_postal_code',
                'shipping_country'
            )
        }),
        ('اطلاعات پرداخت', {
            'fields': ('payment_receipt',)
        }),
        ('مبالغ', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'total')
        }),
        ('یادداشت‌ها', {
            'fields': ('notes',)
        }),
    )
    
    inlines = [OrderItemInline]
    
    def has_add_permission(self, request):
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'product_price', 'subtotal')
    list_filter = ('order__created_date',)
    search_fields = ('order__order_number', 'product_name')
    readonly_fields = ('order', 'product', 'product_name', 'product_price', 'quantity', 'subtotal')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False