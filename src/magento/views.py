from django.views.generic import ListView

from magento.models import BuyOrder


class BuyOrderView(ListView):
    model = BuyOrder
    template_name = 'buyorder_list.html'
    context_object_name = 'buyorders'
    paginate_by = 20
    ordering = '-buy_order'
