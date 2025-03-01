from rest_framework import serializers
from .models import Product,Cart, Order, OrderItem
from django.contrib.auth.models import User, Group

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product 
        fields = '__all__'


#
class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer
    product = ProductSerializer
    class Meta:
        model = Cart
        fields = ['id','user','product','quantity']
    

class OrderItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    # cart_items = CartItemSerializer(source = 'cartitem_set', many=True, read_only = True)

    class Meta:
        model = Order
        fields = '__all__'


