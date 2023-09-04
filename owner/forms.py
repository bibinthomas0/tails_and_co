from django import forms

class OrderStatusFilterForm(forms.Form):
    D = forms.BooleanField(required=False)
    S = forms.BooleanField(required=False)
    O = forms.BooleanField(required=False)
    P = forms.BooleanField(required=False)
    
class OrderReturnStatusFilterForm(forms.Form):
    P = forms.BooleanField(required=False)
    C = forms.BooleanField(required=False)
    R = forms.BooleanField(required=False)