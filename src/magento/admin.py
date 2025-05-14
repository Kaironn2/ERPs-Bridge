from django.contrib import admin

from magento.models import BuyOrder, BuyOrderDetail, Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'customer_external_id',
        'first_name',
        'last_name',
        'email',
        'cpf',
        'phone',
        'customer_group',
        'customer_since',
        'last_purchase',
        'created_at',
        'updated_at',
    )
    search_fields = ('email', 'cpf', 'firs_tname', 'last_name')
    list_filter = ('customer_group', 'customer_since', 'last_purchase')
    ordering = ('-customer_since',)
    list_per_page = 20

    def __str__(self):
        return self.customer_external_id


@admin.register(BuyOrder)
class BuyOrderAdmin(admin.ModelAdmin):
    list_display = ('buy_order', 'created_at', 'updated_at')
    search_fields = ('buy_order',)
    ordering = ('-buy_order',)
    list_per_page = 20

    def __str__(self):
        return str(self.buy_order)


@admin.register(BuyOrderDetail)
class BuyOrderDetailAdmin(admin.ModelAdmin):
    list_display = (
        'customer',
        'buy_order',
        'buy_order_external_id',
        'purchase_date',
        'status',
        'payment_type',
        'shipping_amount',
        'discount_amount',
        'total_amount',
        'created_at',
        'updated_at',
    )
    search_fields = ('email__email', 'buy_order__buy_order')
    list_filter = ('status', 'payment_type')
    ordering = ('-purchase_date',)
    list_per_page = 20

    def __str__(self):
        return str(self.buy_order_external_id)
