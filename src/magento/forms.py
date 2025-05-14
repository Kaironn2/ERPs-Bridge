from django import forms


class BuyOrderFilterForm(forms.Form):
    buyorder = forms.CharField(
        label='Ordem de Compra',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Ordem de Compra'}
        ),
    )
    created_at = forms.CharField(
        label='Criado Em',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Criado Em'}
        ),
    )


class XMLUploadForm(forms.Form):
    xml_file = forms.FileField(label='Arquivo XML', required=True)
