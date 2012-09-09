# -*- coding: utf-8 -*-
from django import forms


class ShoppingCartForm(forms.Form):
    email = forms.EmailField(max_length=254)
    message = forms.CharField(required=False)



