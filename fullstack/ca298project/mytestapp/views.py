from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from django.views.generic import CreateView
from django.http import HttpResponse, HttpResponseRedirect
from .models import Product, CaUser, ShoppingBasket, ShoppingBasketItems, OrderItems
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .permissions import admin_required
from django.contrib.auth.views import LoginView
from http.client import HTTPResponse
from django.contrib.sites import requests
from django.core import serializers
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
import json
from django.forms.models import model_to_dict
from django.core.serializers import serialize
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

class CaUserSignupView(CreateView):
    model = CaUser
    form_class = CASignupForm
    template_name = 'causer_signup.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/')


class AdminSignupView(CreateView):
    model = CaUser
    form_class = AdminSignupForm
    template_name = 'admin_signup.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/')

def index(request):
    return render(request, 'index.html')


def register(request):
    return render(request, 'registration.html')


@login_required
def all_products(request):
    all_p = Product.objects.all()
    flag = request.GET.get('format', '')
    if flag == 'json':
        serialised_products = serializers.serialize('json', all_p)
        return HttpResponse(serialised_products, content_type='application/json')
    else:
        return render(request, 'all_products.html', {'product': all_p})


def singleproduct(request, prodid):
    # prod = Product.objects.get(pk=prodid)
    prod = get_object_or_404(Product, pk=prodid)
    return render(request, 'single_products.html', {'product': prod})

@login_required
@admin_required
def myform(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_product = form.save()
            return render(request, 'single_products.html', {'product': new_product})
    else:
        form = ProductForm()
        return render(request, 'form.html', {'form': form})

def productform(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            new_product = form.save()
            return render(request, 'single_products.html', {'product': new_product})
    else:
        form = ProductForm()
    return render(request, 'productform.html',{'form': form})


class Login(LoginView):
    template_name = 'login.html'


def logout_view(request):
    logout(request)
    return redirect('/')


# @login_required ###
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def add_to_basket(request, prodid):
    user = request.user
    if user.is_anonymous:
        token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]
        user = Token.objects.get(key=token).user
    shopping_basket = ShoppingBasket.objects.filter(user_id=user).first()
    if not shopping_basket:
        shopping_basket = ShoppingBasket(user_id=user).save()
    product = Product.objects.get(pk=prodid)
    sbi = ShoppingBasketItems.objects.filter(basket_id=shopping_basket.id, product_id=product.id).first()
    if sbi is None:
        sbi = ShoppingBasketItems(basket_id=shopping_basket, product_id=product.id).save()
    else:
        sbi.quantity = sbi.quantity + 1
        sbi.save()
    flag = request.GET.get('format', '')
    if flag == 'json':
        return JsonResponse({'status': 'success'})
    else:
        return render(request, 'single_products.html', {'product': product, 'added': True})

# @login_required
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_basket(request):
    user = request.user
    if user.is_anonymous:
        token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]
        user = Token.objects.get(key=token).user
    shopping_basket = ShoppingBasket.objects.filter(user_id=user).first()
    if not shopping_basket:
        # shopping_basket = ShoppingBasket(user_id=user).save()
        shopping_basket, created = ShoppingBasket.objects.get_or_create(user_id=user)
        shopping_basket.save()
    sbi = ShoppingBasketItems.objects.filter(basket_id=shopping_basket.id)
    flag = request.GET.get('format', '')
    if flag == "json":
        basket_array = []
        for basket_item in sbi:
            tmp = {}
            tmp['product'] = basket_item.product.name
            tmp['price'] = float(basket_item.product.price)
            tmp['quantity'] = int(basket_item.quantity)
            basket_array.append(tmp)
        return HttpResponse(json.dumps({'items': basket_array}), content_type="application/json")
    else:
        return render(request, 'shopping_basket.html', {'basket': shopping_basket, 'items': sbi})



@login_required
def remove_from_basket(request, sbi):
    sb = ShoppingBasketItems.objects.get(pk=sbi).delete()
    return redirect('/basket')

#@login_required ###
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def order_form(request):
    user = request.user
    if user.is_anonymous:
        token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]
        user = Token.objects.get(key=token).user
    shopping_basket = ShoppingBasket.objects.filter(user_id=user).first()
    if not shopping_basket:
        return redirect(request, '/')
    sbi = ShoppingBasketItems.objects.filter(basket_id=shopping_basket.id)
    if request.method == 'POST':
        if not request.POST:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            form = OrderForm(body)
        else:
            form = OrderForm(request.POST)
        print(form.errors)

        if form.is_valid():
            order = form.save(commit=False)
            order.user_id = user
            order.save()
            order_items = []
            for basketitem in sbi:
                order_item = OrderItems(order_id=order, product_id=basketitem.product, quantity=basketitem.quantity)
                order_items.append(order_item)

            shopping_basket.delete()
            flag = request.GET.get('format', '')
            if flag == "json":
                return JsonResponse({'status': 'success'})
            else:
                return render(request, 'ordercomplete.html', {'order': order, 'items': order_items})
    else:
        form = OrderForm()
        return render(request, 'orderform.html', {'form': form, 'basket': shopping_basket, 'items': sbi})



# from rest_framework import viewsets
# from .serializers import *
#
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = CaUser.objects.all()
#     serializer_class = UserSerializer

