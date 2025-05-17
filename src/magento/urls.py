from django.urls import path

from magento.views import (
    BuyOrderImportXMLView,
    BuyOrderView,
    CustomerView,
    buy_orders_table,
    customers_table,
)

urlpatterns = [
    path('buyorders/', BuyOrderView.as_view(), name='buy-orders-list'),
    path(
        'buyorders/import/',
        BuyOrderImportXMLView.as_view(),
        name='buy-orders-import',
    ),
    path('buyorders/table/', buy_orders_table, name='buy-orders-table'),
    path('customers/', CustomerView.as_view(), name='customers-list'),
    path('customers/table/', customers_table, name='customers-table'),
]
