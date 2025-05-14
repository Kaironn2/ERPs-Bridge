from django.contrib import admin
from django.urls import path

from core.views import HomeView
from magento.views import BuyOrderView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('buyorders/', BuyOrderView.as_view(), name='buyorder-list'),
]
