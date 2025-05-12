from magento.models import BuyOrder
from parsers.xml_parser import XMLParser


class BuyOrderReportImporter:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.df_orders = XMLParser.xml_2003(self.xml_file, pop_footer=True)
        self.normalize_columns()

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

    def normalize_columns(self):
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
