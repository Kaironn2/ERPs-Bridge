import re

from django.db import transaction

from magento.models import BuyOrder, BuyOrderDetail, Customer
from utils.dataframe_utils import DataframeUtils as dfu
from utils.parsers.xml_parser import XMLParser


class BuyOrderReportImporter:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.df_orders = XMLParser.xml_2003(self.xml_file, pop_footer=True)

    def import_orders(self) -> None:
        self._normalize_columns()
        self._convert_columns_to_date()
        self._convert_str_currency_to_float()
        self._capitalize_columns()
        self._lowercase_columns()
        self._clean_phone_column()
        self.insert_new_buy_order()
        self.upsert_customers()
        self.upsert_buy_order_details()

    def insert_new_buy_order(self):
        report_buy_orders = set(self.df_orders['buy_order'])
        existing_buy_orders = set(
            BuyOrder.objects.filter(
                buy_order__in=report_buy_orders
            ).values_list('buy_order', flat=True)
        )
        new_buy_orders = report_buy_orders - existing_buy_orders
        if new_buy_orders:
            BuyOrder.objects.bulk_create([
                BuyOrder(buy_order=buy_order) for buy_order in new_buy_orders
            ])

    def upsert_buy_order_details(self):
        with transaction.atomic():
            for _, row in self.df_orders.iterrows():
                row_data = row.to_dict()

                buy_order_number = row_data.pop('buy_order')
                buy_order_instance = BuyOrder.objects.get(buy_order=buy_order_number)

                email = row_data.pop('email')
                customer_instance = Customer.objects.get(email=email)

                BuyOrderDetail.objects.update_or_create(
                    buy_order=buy_order_instance,
                    email=customer_instance,
                    defaults=row_data
                )

    def upsert_customers(self) -> None:
        for _, row in self.df_orders.iterrows():
            row_data = row.to_dict()
            email = row_data.get('email')
            cpf = row_data.get('cpf')

            customer = None

            if email:
                customer = Customer.objects.filter(email=email).first()
            if not customer and cpf:
                customer = Customer.objects.filter(cpf=cpf).first()

            if customer:
                for field, value in row_data.items():
                    if hasattr(customer, field):
                        setattr(customer, field, value)
                customer.save()
            else:
                Customer.objects.create(**row_data)

    def _normalize_columns(self) -> None:
        self.df_orders.columns = [
            col.replace(' ', '_').lower() for col in self.df_orders.columns
        ]
        self.df_orders.rename(
            columns={
                'pedido_#': 'buy_order',
                'id_do_pedido': 'buy_order_external_id',
                'firstname': 'first_name',
                'lastname': 'last_name',
                'email': 'email',
                'grupo_do_cliente': 'customer_group',
                'número_cpf/cnpj': 'cpf',
                'comprado_em': 'purchase_date',
                'shipping_telephone': 'phone',
                'status': 'status',
                'payment_type': 'payment_type',
                'qtd._vendida': 'quantity_sold',
                'frete': 'shipping_amount',
                'desconto': 'discount_amount',
                'total_da_venda': 'total_amount',
            },
            inplace=True,
        )

    def _convert_columns_to_date(self) -> None:
        date_columns = [
            'purchase_date',
        ]
        self.df_orders = dfu.columns_to_date(
            self.df_orders, date_columns, date_format='%d/%m/%Y %H:%M:%S'
        )

    def _convert_str_currency_to_float(self) -> None:
        float_columns = [
            'shipping_amount',
            'discount_amount',
            'total_amount',
        ]
        for column in float_columns:
            self.df[column] = self.df[column].str.replace(
                'R$', '', regex=False
            )
            self.df[column] = self.df[column].str.replace('.', '', regex=False)
            self.df[column] = self.df[column].str.replace(
                ',', '.', regex=False
            )
            self.df[column] = self.df[column].astype(float)

    def _capitalize_columns(self) -> None:
        capitalize_columns = ['first_name', 'last_name']
        for column in capitalize_columns:
            self.df_orders[column] = self.df_orders[column].str.capitalize()

    def _lowercase_columns(self) -> None:
        lowercase_columns = [
            'customer_group',
            'status',
            'payment_type',
            'email',
        ]
        for column in lowercase_columns:
            self.df_orders[column] = self.df_orders[column].str.lower()

    def _clean_phone_column(self) -> None:
        if 'phone' in self.df_orders.columns:
            self.df_orders['phone'] = (
                self.df_orders['phone']
                .astype(str)
                .apply(lambda x: re.sub(r'\D', '', x))
            )
