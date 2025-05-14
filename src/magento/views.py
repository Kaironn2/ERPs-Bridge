from django.views.generic import ListView

from magento.forms import BuyOrderFilterForm
from magento.models import BuyOrder


class BuyOrderView(ListView):
    model = BuyOrder
    template_name = 'buyorder_list.html'
    context_object_name = 'buyorders'
    paginate_by = 20
    ordering = '-buy_order'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter_form = BuyOrderFilterForm(self.request.GET)
        if self.filter_form.is_valid():
            buyorder = self.filter_form.cleaned_data.get('buyorder')
            created_at = self.filter_form.cleaned_data.get('created_at')

            if buyorder:
                queryset = queryset.filter(buy_order__icontains=buyorder)
            if created_at:
                queryset = queryset.filter(created_at__icontains=created_at)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = getattr(
            self, 'filter_form', BuyOrderFilterForm()
        )
        return context
