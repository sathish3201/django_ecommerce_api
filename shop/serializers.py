from rest_framework import serializers
from .models import Product,Cart, Order, Delivery
from django.contrib.auth.models import User, Group
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.template.loader import render_to_string

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product 
        fields = '__all__'

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ['id','fname','lname','email','mobileno','address','country','state','city','zip']
#
class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Cart
        fields = ['id','product','quantity']
    

class OrderSerializer(serializers.ModelSerializer):
    user= UserSerializer()
    cart= CartSerializer(many=True)
    delivery_detail = DeliverySerializer()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        model = Order
        fields = ['id','user','cart','delivery_detail','total_price']

    


        

