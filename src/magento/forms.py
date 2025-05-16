from django import forms


class BuyOrderFilterForm(forms.Form):
    buy_order = forms.CharField(
        label='Ordem de Compra',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Pesquisar...'}
        ),
    )
    purchase_date = forms.CharField(
        label='Data de Compra',
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        ),
    )



class XMLUploadForm(forms.Form):
    xml_file = forms.FileField(label='Arquivo XML', required=True)
