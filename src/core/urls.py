from django.contrib import admin
from django.urls import path

from core.views import HomeView
from magento.views import BuyOrderImportXMLView, BuyOrderView, buy_orders_table

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('buyorders/', BuyOrderView.as_view(), name='buy-orders-list'),
    path(
        'buyorders/import/',
        BuyOrderImportXMLView.as_view(),
        name='buy-orders-import',
    ),
    path('buyorders/table/', buy_orders_table, name='buy-orders-table'),
]
