from django.forms import ModelForm, ModelChoiceField
from .models import Product, CaUser, Order # ProductCategory,
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction


# class CategoryChoiceField(ModelChoiceField):
#     def label_from_instance(self, obj):
#         return obj.name


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'picture'] # 'category'


class CASignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CaUser

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_admin = False
        user.save()
        return user


class AdminSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CaUser

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_admin = True
        user.save()
        return user


from django import forms
from django.contrib.auth.forms import AuthenticationForm


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
    username = forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'hello'})
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'hi'}))

class OrderForm(ModelForm):
    shipping_addr = forms.CharField(label="Shipping Address", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'hi again'}))
    class Meta:
        model = Order
        fields = ['shipping_addr']
