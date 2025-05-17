import pandas as pd
from django.db import transaction

from magento.models import BuyOrder, BuyOrderDetail, Customer


def insert_new_buy_orders(buy_orders: list) -> None:
    if buy_orders:
        new_instances = [
            BuyOrder(buy_order=buy_order) for buy_order in buy_orders
        ]
        BuyOrder.objects.bulk_create(new_instances, ignore_conflicts=True)


def upsert_customers_from_df(df: pd.DataFrame) -> None:
    model_fields = {
        'first_name',
        'last_name',
        'email',
        'cpf',
        'phone',
        'customer_group',
        'last_purchase',
    }

    df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')

    with transaction.atomic():
        for _, row in df.iterrows():
            email = row.get('email')
            cpf = row.get('cpf')
            purchase_date = row.get('purchase_date')

            customer = Customer.objects.filter(email=email).first()

            if not customer:
                customer = Customer.objects.filter(cpf=cpf).first()

            customer_data = {k: row[k] for k in model_fields if k in row}

            if customer:
                if purchase_date:
                    if (
                        not customer.last_purchase
                        or purchase_date > customer.last_purchase
                    ):
                        customer.last_purchase = purchase_date
                        customer.save(update_fields=['last_purchase'])
                continue

            customer_data['last_purchase'] = purchase_date

            Customer.objects.create(**customer_data)


def upsert_buy_orders_details(df: pd.DataFrame) -> None:
    with transaction.atomic():
        for _, row in df.iterrows():
            customer = Customer.objects.filter(email=row['email']).first()
            buy_order = BuyOrder.objects.filter(
                buy_order=row['buy_order']
            ).first()

            if not (customer and buy_order):
                continue

            detail_defaults = {
                'buy_order_external_id': row['buy_order_external_id'],
                'purchase_date': row['purchase_date'],
                'status': row['status'],
                'payment_type': row['payment_type'],
                'shipping_amount': row['shipping_amount'],
                'discount_amount': row['discount_amount'],
                'total_amount': row['total_amount'],
                'customer': customer,
            }

            BuyOrderDetail.objects.update_or_create(
                buy_order=buy_order, defaults=detail_defaults
            )
