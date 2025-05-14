import re

from django.db import transaction

from magento.models import BuyOrder, BuyOrderDetail, Customer
from utils.dataframe_utils import DataframeUtils as dfu
from utils.parsers.xml_parser import XMLParser
from django.db import models
from django.db.models import Field


class BuyOrderReportImporter:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.df_orders = XMLParser.xml_2003(self.xml_file, pop_footer=True)
        print(f'Linhas carregadas: {len(self.df_orders)}')

    def import_orders(self) -> None:
        print('Importando ordens de compra...')
        self._normalize_columns()
        self._convert_columns_to_date()
        self._convert_str_currency_to_float()
        self._capitalize_columns()
        self._lowercase_columns()
        self._clean_phone_column()
        self._insert_new_buy_order()
        self._upsert_customers()
        self._upsert_buy_order_details()

    def _insert_new_buy_order(self):
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

    def _upsert_buy_order_details(self):
        model_fields = {f.name for f in BuyOrderDetail._meta.get_fields() if not f.is_relation}
        required_fields = [
            'buy_order_external_id',
            'purchase_date',
            'status',
            'payment_type',
            'shipping_amount',
            'discount_amount',
            'total_amount',
        ]

        with transaction.atomic():
            for index, row in self.df_orders.iterrows():
                row_data_original_for_log = row.to_dict()
                row_data = row_data_original_for_log.copy()

                buy_order_number = row_data.pop('buy_order', None)
                email_for_customer_lookup = row_data.pop('email', None)
                cpf_for_customer_lookup = row_data.get('cpf', None)

                if buy_order_number is None:
                    print(f"AVISO (Linha {index+2}): 'buy_order' não encontrado. Dados: {row_data_original_for_log}")
                    continue

                try:
                    buy_order_instance = BuyOrder.objects.get(buy_order=buy_order_number)
                except BuyOrder.DoesNotExist:
                    print(f"ERRO CRÍTICO (Linha {index+2}): BuyOrder '{buy_order_number}' não existe. Dados: {row_data_original_for_log}")
                    continue

                customer_instance = self._find_customer(email_for_customer_lookup, cpf_for_customer_lookup)
                if not customer_instance:
                    print(
                        f"ERRO (Linha {index+2}): Cliente não encontrado "
                        f"(email: '{email_for_customer_lookup}', cpf: '{cpf_for_customer_lookup}'). "
                        f"Dados: {row_data_original_for_log}"
                    )
                    continue

                final_detail_data = {k: row_data.get(k) for k in required_fields if k in model_fields}

                missing_required = [k for k in required_fields if final_detail_data.get(k) is None]
                if missing_required:
                    print(f"ERRO (Linha {index+2}): Faltando campos obrigatórios: {missing_required}. Dados: {row_data_original_for_log}")
                    continue

                try:
                    BuyOrderDetail.objects.update_or_create(
                        buy_order_external_id=final_detail_data['buy_order_external_id'],
                        defaults={
                            'buy_order': buy_order_instance,
                            'customer': customer_instance,
                            **final_detail_data
                        },
                    )
                except Exception as e:
                    print(f"ERRO AO SALVAR DETAIL (Linha {index+2}): {e}. Dados: {final_detail_data} | Originais: {row_data_original_for_log}")

    def _find_customer(
        self, email: str | None, cpf: str | None
    ) -> Customer | None:
        customer_instance = None
        if email:
            customer_instance = Customer.objects.filter(email=email).first()
        if not customer_instance and cpf:
            customer_instance = Customer.objects.filter(cpf=cpf).first()
        return customer_instance

    def _update_customer_record(
        self,
        customer_instance: Customer,
        payload: dict,
        purchase_date_from_row,
    ) -> None:
        for field_name, value in payload.items():
            if field_name != 'last_purchase':
                setattr(customer_instance, field_name, value)

        if purchase_date_from_row:
            if hasattr(customer_instance, 'last_purchase'):
                if (
                    customer_instance.last_purchase is None
                    or purchase_date_from_row > customer_instance.last_purchase
                ):
                    customer_instance.last_purchase = purchase_date_from_row
            else:
                print(
                    "AVISO: Modelo Customer não possui o atributo 'last_purchase'. "
                    'Verifique a definição do modelo.'
                )
        try:
            customer_instance.save()
        except Exception as e:
            email_val = getattr(customer_instance, 'email', 'N/A')
            cpf_val = getattr(customer_instance, 'cpf', 'N/A')
            print(
                f'Erro ao ATUALIZAR customer: {e}, email: {email_val}, cpf: {cpf_val}'
            )

    def _create_customer_record(
        self, payload: dict, purchase_date_from_row, customer_fields: set
    ) -> None:
        if purchase_date_from_row and 'last_purchase' in customer_fields:
            payload['last_purchase'] = purchase_date_from_row

        valid_payload = {
            k: v for k, v in payload.items() if k in customer_fields
        }

        try:
            Customer.objects.create(**valid_payload)
        except Exception as e:
            email_val = payload.get('email', 'N/A')
            cpf_val = payload.get('cpf', 'N/A')
            print(
                f'Erro ao CRIAR customer: {e}, email: {email_val}, cpf: {cpf_val}, dados: {valid_payload}'
            )

    def _upsert_customers(self) -> None:
        customer_fields = {field.name for field in Customer._meta.get_fields()}

        for _, row in self.df_orders.iterrows():
            row_data = row.to_dict()
            email = row_data.get('email')
            cpf = row_data.get('cpf')
            purchase_date = row_data.get('purchase_date')

            customer_payload_for_model = {
                k: v
                for k, v in row_data.items()
                if k in customer_fields and k != 'last_purchase'
            }
            if 'email' in customer_fields and email:
                customer_payload_for_model['email'] = email
            if 'cpf' in customer_fields and cpf:
                customer_payload_for_model['cpf'] = cpf

            customer_instance = self._find_customer(email, cpf)

            if customer_instance:
                self._update_customer_record(
                    customer_instance,
                    customer_payload_for_model,
                    purchase_date,
                )
            else:
                self._create_customer_record(
                    row_data.copy(), purchase_date, customer_fields
                )

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
