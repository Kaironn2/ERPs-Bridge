from django.contrib import admin
from django.urls import path

from mgt.models import MgtCustomer, BuyOrder, BuyOrderDetail


@admin.register(MgtCustomer)
class MgtCustomerAdmin(admin.ModelAdmin):
    list_display = (
        'customer_external_id', 'first_name', 'last_name', 'email', 'cpf', 'phone', 
        'customer_group', 'customer_since', 'last_purchase', 'created_at', 'updated_at'
    )
    search_fields = ('email', 'cpf', 'first_name', 'last_name')
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

    change_list_template = 'admin/mgt/buy_order_details_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-xml/', self.admin_site.admin_view(self.import_xml), name='buyorderdetails-import-xml'),
        ]
        return custom_urls + urls
    
    def import_xml(self, request):
        pass
    

@admin.register(BuyOrderDetail)
class BuyOrderDetailAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'buy_order', 'buy_order_external_id', 'purchase_date', 
        'status', 'payment_type', 'shipping_amount', 'discount_amount', 
        'total_amount', 'created_at', 'updated_at'
    )
    search_fields = ('email__email', 'buy_order__buy_order')
    list_filter = ('status', 'payment_type')
    ordering = ('-purchase_date',)
    list_per_page = 20

    def __str__(self):
        return str(self.buy_order_external_id)
