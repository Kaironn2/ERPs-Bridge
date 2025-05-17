import django.db
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from magento.forms import BuyOrderFilterForm, CustomerFilterForm, XMLUploadForm
from magento.models import BuyOrder, Customer
from magento.reports import BuyOrderReportImporter

BUY_ORDERS_PAGINATE_BY = 50
CUSTOMERS_PAGINATE_BY = 50


class CustomerView(ListView):
    """View to list customers with filtering and pagination."""

    model = Customer
    template_name = 'customers_list.html'
    context_object_name = 'customers'
    paginate_by = CUSTOMERS_PAGINATE_BY
    ordering = '-last_purchase'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter_form = CustomerFilterForm(self.request.GET)
        if self.filter_form.is_valid():
            first_name = self.filter_form.cleaned_data.get('first_name')
            email = self.filter_form.cleaned_data.get('email')
            customer_group = self.filter_form.cleaned_data.get(
                'customer_group'
            )

            if first_name:
                queryset = queryset.filter(first_name__icontains=first_name)
            if email:
                queryset = queryset.filter(email__icontains=email)
            if customer_group:
                queryset = queryset.filter(
                    customer_group__icontains=customer_group
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = getattr(
            self, 'filter_form', CustomerFilterForm()
        )
        return context


def customers_table(request):
    """Render the customers table with pagination and filtering using AJAX."""
    queryset = Customer.objects.all().order_by('-last_purchase')
    filter_form = BuyOrderFilterForm(request.GET)
    if filter_form.is_valid():
        first_name = filter_form.cleaned_data.get('first_name')
        email = filter_form.cleaned_data.get('email')
        customer_group = filter_form.cleaned_data.get('customer_group')

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if email:
            queryset = queryset.filter(email__icontains=email)
        if customer_group:
            queryset = queryset.filter(
                customer_group__icontains=customer_group
            )

    paginator = Paginator(queryset, CUSTOMERS_PAGINATE_BY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'partials/customers_table.html',
        {
            'customers': page_obj.object_list,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        },
    )


class BuyOrderView(ListView):
    """View to list buy orders with filtering and pagination."""

    model = BuyOrder
    template_name = 'buy_orders_list.html'
    context_object_name = 'buyorders'
    paginate_by = BUY_ORDERS_PAGINATE_BY
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
    """View to handle the import of XML files for buy orders."""

    template_name = 'buy_orders_import_xml.html'
    form_class = XMLUploadForm
    success_url = reverse_lazy('buy-orders-import')

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
            except django.db.utils.OperationalError as e:
                messages.error(
                    self.request, f'Erro de banco de dados: {str(e)}'
                )
                files_error_count += 1
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
    """Render the buy orders table with pagination and filtering using AJAX."""
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

    paginator = Paginator(queryset, BUY_ORDERS_PAGINATE_BY)
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
