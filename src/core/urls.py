from django.contrib import admin
from django.urls import path

from magento.views import BuyOrderView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('buyorders/', BuyOrderView.as_view(), name='buyorder-list'),
]
