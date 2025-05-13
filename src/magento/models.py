from django.db import models


class Customer(models.Model):
    customer_external_id = models.IntegerField(
        unique=True, blank=True, null=True
    )
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    cpf = models.CharField(max_length=11, unique=True)
    phone = models.CharField(max_length=20)
    customer_group = models.CharField(max_length=255, blank=True, null=True)
    customer_since = models.DateTimeField(blank=True, null=True)
    last_purchase = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['cpf']),
            models.Index(fields=['cpf', 'email']),
        ]

    def __str__(self):
        return self.email


class BuyOrder(models.Model):
    buy_order = models.IntegerField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-buy_order']
        verbose_name = 'Ordem de Compra'
        verbose_name_plural = 'Ordens de Compra'
        indexes = [
            models.Index(fields=['buy_order']),
        ]

    def __str__(self):
        return str(self.buy_order)


class BuyOrderDetail(models.Model):
    email = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name='buy_order_detail'
    )
    buy_order = models.ForeignKey(
        BuyOrder, on_delete=models.PROTECT, related_name='buy_order_detail'
    )
    buy_order_external_id = models.IntegerField(unique=True)
    purchase_date = models.DateTimeField()
    status = models.CharField(max_length=255)
    payment_type = models.CharField(max_length=255)
    quantity_sold = models.IntegerField()
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-purchase_date']
        verbose_name = 'Detalhes da Ordem de Compra'
        verbose_name_plural = 'Detalhes das Ordens de Compra'

        indexes = [
            models.Index(fields=['email'], name='buyorderdetail_email_idx'),
            models.Index(
                fields=['buy_order'], name='buyorderdetail_buy_order_idx'
            ),
        ]

    def __str__(self):
        return str(self.buy_order_external_id)
