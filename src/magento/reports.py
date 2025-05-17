import re

from magento.repositories import (
    insert_new_buy_orders,
    upsert_buy_orders_details,
    upsert_customers_from_df,
)
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
        self._format_payment_type()
        self._clean_phone_column()
        self._clean_cpf_column()
        self._import_buy_orders()
        self._import_customers()
        self._import_buy_orders_details()

    def _import_buy_orders(self):
        insert_new_buy_orders(self.df_orders['buy_order'].to_list())

    def _import_customers(self):
        upsert_customers_from_df(self.df_orders)

    def _import_buy_orders_details(self):
        upsert_buy_orders_details(self.df_orders)

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
            self.df_orders[column] = self.df_orders[column].str.replace(
                'R$', '', regex=False
            )
            self.df_orders[column] = self.df_orders[column].str.replace(
                '.', '', regex=False
            )
            self.df_orders[column] = self.df_orders[column].str.replace(
                ',', '.', regex=False
            )
            self.df_orders[column] = self.df_orders[column].astype(float)

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

    def _clean_cpf_column(self) -> None:
        if 'cpf' in self.df_orders.columns:
            self.df_orders['cpf'] = (
                self.df_orders['cpf']
                .astype(str)
                .apply(lambda x: re.sub(r'\D', '', x))
            )

    def _format_payment_type(self) -> None:
        if 'payment_type' in self.df_orders.columns:
            self.df_orders['payment_type'] = self.df_orders[
                'payment_type'
            ].replace('não é necessário efetuar um pagamento.', 'saldo')
