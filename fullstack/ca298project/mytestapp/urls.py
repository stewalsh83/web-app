from django.urls import path, include
from . import views
from .forms import UserLoginForm, OrderForm
from django.conf.urls import url
from rest_framework import routers, serializers, viewsets
from .models import CaUser, Product
from rest_framework.authtoken.views import obtain_auth_token

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CaUser
        fields = ['url', 'username', 'email', 'is_staff']

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'picture']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = []
    permission_classes = []

class UserViewSet(viewsets.ModelViewSet):
    queryset = CaUser.objects.all()
    serializer_class = UserSerializer

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.register, name='register'),
    path('allproducts/', views.all_products, name="all products"), # admin locked
    path('singleproduct/<int:prodid>', views.singleproduct, name='product_single'),
    path('myform/', views.myform),
    path('usersignup/', views.CaUserSignupView.as_view(), name='register'),
    path('adminsignup/',views.AdminSignupView.as_view(), name='Admin register'),
    path('login/', views.Login.as_view(template_name='login.html', authentication_form=UserLoginForm), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('addbasket/<int:prodid>', views.add_to_basket, name='add_to_basket'), # after click on buy
    path('basket/', views.get_basket, name='basket'), # shopping basket link
    path('basketremove/<int:sbi>', views.remove_from_basket, name='remove_basket'),
    path('checkout/', views.order_form, name='checkout'),
    path('api/', include(router.urls)),
    path('token/', obtain_auth_token, name='api_token_auth')
]
