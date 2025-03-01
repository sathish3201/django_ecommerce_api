from rest_framework import viewsets, status
from .models import Product, Order, Cart, OrderItem
from .serializers import ProductSerializer, OrderSerializer, CartSerializer, UserSerializer, OrderItemSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User, Group
from rest_framework.decorators import action
from django.db import transaction
from rest_framework import permissions 

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="admin").exists()

class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name = "vendor").exists()
    
class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name = "customer").exists()

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    @action(detail= True, methods=['get'] , url_path='get_by_id')
    def get_product_by_id(self, request, *args, **kwargs):
        ''' get by id'''
        prodid = int(kwargs.get('pk'))

        try:
            product = Product.objects.get(id = prodid)
        except Product.DoesNotExist:
            return Response({"detail": f"Product not found {prodid}"})
        return Response({"product": ProductSerializer(product).data})

   
   

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


        
    @action(detail= True, methods=['post'], url_path='place-order')
    @transaction.atomic
    def place_order(self, request, *args, **kwargs):
        ''' place order by transfering cart items  to the order'''
         # get specific order
        userid = int(kwargs.get('pk'))

        if userid != request.user.id:
            return Response({"detail": "you cannot place order of another user..","user":request.user.id,},status= status.HTTP_400_BAD_REQUEST)
        cart = Cart.objects.filter(user = request.user)

        if not cart:
            return Response({"error": "Cart is Empty"}, status= status.HTTP_404_NOT_FOUND)
        # check all product quantity less than stack
        for item in cart.all():
            try:
                product = Product.objects.get(id = item.product.id)
                if product.stock < item.quantity:
                    return Response({"detail":f"quantity should be less than stock , stock  is {product.stock} for product {product.name}"})
            except Product.DoesNotExist:
                return Response({"error":f"product not found {item.product}"},status= status.HTTP_404_NOT_FOUND)
            
        # create new order
        order = Order.objects.create(
            user = request.user,
            status = "pending",
            total_price= sum(item.product.price*item.quantity for item in cart.all())
        )
        # add order to cart item  to order
        for item in cart.all():
            OrderItem.objects.create(
                order  = order,
                product = item.product,
                quantity = item.quantity,
                price = item.product.price * item.quantity
            )
        # clear all items
        cart.all().delete()
        return Response({"detail": f"Order Placed Successfully with order id : {order.id}"})
        # cart_items = Cart.objects.filter(user = userid)
        # return Response({"message": cart_}, status=status.HTTP_201_CREATED)

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    @action(detail= True, methods=['get'])
    def checkout(self, request,*args, **kwargs):
        userid = int(kwargs.get('pk'))
        if userid != request.user.id:
            return Response({"detail": "you cannot place order of another user..","user":request.user.id,},status= status.HTTP_400_BAD_REQUEST)
        try:
            cart = Cart.objects.filter(user = request.user)

        except Cart.DoesNotExist:
            return Response({"detail": "you is empty"},status=status.HTTP_404_NOT_FOUND)
        for item in cart.all():
            try:
                product = Product.objects.get(id = item.product.id)
                if product.stock < item.quantity:
                    item.delete()
                    return Response({"detail":f"quantity should be less than stock , stock  is {product.stock} for product {product.name}"})
            except Product.DoesNotExist:
                return Response({"error":f"product not found {item.product}"},status= status.HTTP_404_NOT_FOUND)
        # cart.all().filter(lambda x: x.quantity > x.product.stock).delete()
        
        total_price = sum(item.quantity * item.product.price for item in cart.all())
        return Response({"total_price":total_price})
        
        
# creating jwt token view
from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework import status 

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    @transaction.atomic
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role','customer') # Default role is 'Customer'
        # Validate the role 
        valid_role = ['admin','customer','vendor']
        if role not in valid_role:
            return Response({"error": "Invalid role. Choose from 'Admin', 'Customer', 'Vendor'."},
                            status= status.HTTP_400_BAD_REQUEST)
        # create user and assign the password
        user = User.objects.create(username = username, email = email)
        user.set_password(password)
        # assign the role to the user by adding the user to the appropriate group 
        group, created = Group.objects.get_or_create(name = role)
        user.groups.add(group)

        # save the user
        user.save()
        return Response({"message":f"User created with role {role}"}, status= status.HTTP_201_CREATED)
    http_method_names = ['post']

class LoginAPIView(APIView):
    #  grant permissions
    permission_classes = [AllowAny]
    @transaction.atomic
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password').strip()

        user = User.objects.filter(username = username).first()
        # if user:
        #     return Response({"message": f"user found:{user.username} with password {user.password} with {user.check_password(password)} given {password}"},status= status.HTTP_200_OK)
        if user and user.check_password(password):
            # create the jwt token for user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            #get the user's role 
            roles = [group.name for group in user.groups.all()]
            return Response({
                "user_role": {
                    "user":UserSerializer(user).data,
                     "access_token" : str(access_token),
                     "refresh_token": str(refresh),
                    "roles" : roles
                },
              
            }, status= status.HTTP_200_OK)
        
        return Response({
            "error": "Invalid credentials"
        }, status= 400)
    http_method_names = ['post']

# admin only view


class CustomerOnlyView(APIView):
    permission_classes= [AllowAny]

    def get(self, request):
        return Response({"message": "view for only customers"})


class SomeAdminOnlyView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({"message": "view for admins only..."})



