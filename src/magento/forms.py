from django import forms

from magento.models import BuyOrderDetail, Customer


class BuyOrderFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_choices()
        self.payment_type_choices()

    buy_order = forms.CharField(
        label='Ordem de Compra',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Pesquisar...'}
        ),
    )
    purchase_date = forms.DateField(
        label='Data de Compra',
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        ),
    )
    status = forms.ChoiceField(
        label='Status',
        required=False,
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    payment_type = forms.ChoiceField(
        label='Método de Pagamento',
        required=False,
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def status_choices(self):
        status_choices = set(
            BuyOrderDetail.objects.values_list('status', flat=True).distinct()
        )
        status_choices = [(s, s) for s in status_choices if s]
        self.fields['status'].choices = [('', 'Todos')] + status_choices

    def payment_type_choices(self):
        payment_type_choices = set(
            BuyOrderDetail.objects.values_list(
                'payment_type', flat=True
            ).distinct()
        )
        payment_type_choices = [(s, s) for s in payment_type_choices if s]
        self.fields['payment_type'].choices = [
            ('', 'Todos')
        ] + payment_type_choices


class XMLUploadForm(forms.Form):
    xml_file = forms.FileField(label='Arquivo XML', required=True)


class CustomerFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer_group_choices()

    first_name = forms.CharField(
        label='Nome',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Pesquisar...'}
        ),
    )
    email = forms.DateField(
        label='E-mail',
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        ),
    )
    customer_group = forms.ChoiceField(
        label='Grupo do Cliente',
        required=False,
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def customer_group_choices(self):
        customer_group_choices = set(
            Customer.objects.values_list(
                'customer_group', flat=True
            ).distinct()
        )
        customer_group_choices = [(s, s) for s in customer_group_choices if s]
        self.fields['customer_group'].choices = [
            ('', 'Todos')
        ] + customer_group_choices
