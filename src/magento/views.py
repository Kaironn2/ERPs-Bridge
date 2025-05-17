from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import FormView, ListView

from magento.forms import BuyOrderFilterForm, XMLUploadForm
from magento.models import BuyOrder
from magento.reports import BuyOrderReportImporter


class BuyOrderView(ListView):
    model = BuyOrder
    template_name = 'buy_orders_list.html'
    context_object_name = 'buyorders'
    paginate_by = 20
    ordering = '-buy_order'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter_form = BuyOrderFilterForm(self.request.GET)
        if self.filter_form.is_valid():
            buy_order = self.filter_form.cleaned_data.get('buy_order')
            purchase_date = self.filter_form.cleaned_data.get('purchase_date')
            status = self.filter_form.cleaned_data.get('status')
            payment_type = self.filter_form.cleaned_data.get('payment_type')

            if buy_order:
                queryset = queryset.filter(buy_order__icontains=buy_order)
            if purchase_date:
                queryset = queryset.filter(
                    buy_order_detail__purchase_date__icontains=purchase_date
                )
            if status:
                queryset = queryset.filter(buy_order_detail__status=status)
            if payment_type:
                queryset = queryset.filter(
                    buy_order_detail__payment_type=payment_type
                )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = getattr(
            self, 'filter_form', BuyOrderFilterForm()
        )
        return context


class BuyOrderImportXMLView(FormView):
    template_name = 'buy_orders_import_xml.html'
    form_class = XMLUploadForm
    success_url = '/buyorders/import/'

    def form_valid(self, form):
        xml_files = self.request.FILES.getlist('xml_file')
        files_success_count = 0
        files_error_count = 0
        error_messages = []

        if not xml_files:
            messages.error(self.request, 'Nenhum arquivo foi selecionado.')
            return super().form_invalid(form)

        for xml_file in xml_files:
            try:
                importer = BuyOrderReportImporter(xml_file)
                importer.import_orders()
                files_success_count += 1
            except Exception as e:
                error_message = (
                    f'Erro ao processar o arquivo {xml_file.name}: {str(e)}.'
                )
                messages.error(self.request, error_message)
                error_messages.append(error_message)
                files_error_count += 1

        if files_success_count > 0:
            messages.success(
                self.request,
                f'{files_success_count} arquivo(s) importado(s) com sucesso!',
            )

        return super().form_valid(form)


def buy_orders_table(request):
    queryset = BuyOrder.objects.all().order_by('-buy_order')
    filter_form = BuyOrderFilterForm(request.GET)
    if filter_form.is_valid():
        buy_order = filter_form.cleaned_data.get('buy_order')
        purchase_date = filter_form.cleaned_data.get('purchase_date')
        status = filter_form.cleaned_data.get('status')
        payment_type = filter_form.cleaned_data.get('payment_type')

        if buy_order:
            queryset = queryset.filter(buy_order__icontains=buy_order)
        if purchase_date:
            queryset = queryset.filter(
                buy_order_detail__purchase_date__icontains=purchase_date
            )
        if status:
            queryset = queryset.filter(buy_order_detail__status=status)
        if payment_type:
            queryset = queryset.filter(
                buy_order_detail__payment_type=payment_type
            )

    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'partials/buy_orders_table.html',
        {
            'buyorders': page_obj.object_list,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        },
    )
