from rest_framework import viewsets, status
from .models import Product, Order, Cart,Delivery
from .serializers import ProductSerializer, OrderSerializer, CartSerializer, UserSerializer,DeliverySerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.models import User, Group
from rest_framework.decorators import action
from django.db import transaction
from rest_framework import permissions 
from django.shortcuts import render
# 
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail,EmailMessage 

from django.conf import settings

from django.template.loader import render_to_string 
from django.utils.encoding import force_bytes

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
    permission_classes = [AllowAny]

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
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        orderid = kwargs.get('pk')
        try:
             
            instace = get_object_or_404(Order, id= orderid)
            instace.delete()
        except Exception as e:
            return Response({'detail': f"unable delete your order as :{e}"},status= status.HTTP_404_NOT_FOUND)
        return Response({'detail': f'successfully deleted order id:{orderid}'},status= status.HTTP_200_OK)
    

    @action(detail= True, methods=['post'] , url_path='place-order')
    @transaction.atomic
    def place_order(self, request, *args, **kwargs):
        ''' get by id'''
        userid = int(kwargs.get('pk'))
        if request.user.id != userid:
            return Response({'detail':'UnAuthorized to change'},status=status.HTTP_403_FORBIDDEN)
        
        try:
            serializer= request.data.get('delivery_detail')
            
            delivery_detail = Delivery.objects.create(fname = serializer['fname'], lname = serializer['lname'], email = serializer['email'],
                                                      mobileno = serializer['mobileno'], address = serializer['address'], country = serializer['country'], state = serializer['state'], 
                                                      city = serializer['city'], zip=serializer['zip'])
        except Exception:
            return Response({'detail':'error in creating Delivery'},status= status.HTTP_404_NOT_FOUND)
        print(request.data.get('cart_items'))

        cart_items=[]
        try:
            for item in request.data.get('cart_items'):
                print(item)
                product = Product.objects.get(id = item['product']['id'])
             
                cart_items.append(Cart.objects.create(product = product, quantity = item['quantity']))
        except Exception:
            return Response({'detail': 'error in creating cart'},status=status.HTTP_404_NOT_FOUND)
        
        order = Order.objects.create(user = request.user, delivery_detail = delivery_detail)
        order.cart.set(cart_items)
        return Response({'detail':f"successfulll with order id {order.id}"},status= status.HTTP_201_CREATED)
    
        
    
       

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
        
# creating jwt token view
from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework import status 

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    @transaction.atomic
    def post(self, request):
        try:
            fname = request.data.get('fname')
            lname = request.data.get('lname')
            email = request.data.get('email')
            username = request.data.get('username')
            password = request.data.get('password')
            # role = request.data.get('role','customer') # Default role is 'Customer'
            # Validate the role 
            print(fname, lname, email, password)
            # valid_role = ['admin','customer','vendor']
            # if role not in valid_role:
            #     return Response({"error": "Invalid role. Choose from 'Admin', 'Customer', 'Vendor'."},
            #                     status= status.HTTP_400_BAD_REQUEST)
            # create user and assign the password
            user = User.objects.create(username = username, email=email)
            user.first_name = fname
            user.last_name = lname
            user.set_password(password)
            # assign the role to the user by adding the user to the appropriate group 
            # group, created = Group.objects.get_or_create(name = role)
            # user.groups.add(group)

            # save the user
            user.save()
            return Response({"detail":f"User created with role {username} Successfull"}, status= status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": f"Error in Creating User with user name: {e}"})
    http_method_names = ['post']

class LoginAPIView(APIView):
    #  grant permissions
    permission_classes = [AllowAny]
    @transaction.atomic
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password').strip()

        user = User.objects.filter(email = email).first()
        # if user:
        #     return Response({"message": f"user found:{user.username} with password {user.password} with {user.check_password(password)} given {password}"},status= status.HTTP_200_OK)
        if user and user.check_password(password):
            # create the jwt token for user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            #get the user's role 
            # roles = [group.name for group in user.groups.all()]
            return Response({
                "user_role": {
                    "user":UserSerializer(user).data,
                     "access_token" : str(access_token),
                     "refresh_token": str(refresh),
                  
                },
              
            }, status= status.HTTP_200_OK)
        
        return Response({
            "error": "Invalid credentials"
        }, status= 400)
    http_method_names = ['post']    


class ContactApiView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        print(request.data)
        user_email = request.data.get('email')
        subject  = request.data.get('subject')
        message = request.data.get('message')
    
        if user_email and subject and message:
            try:
                send_mail(subject= subject, message= message, from_email="abc@gmail.com" ,recipient_list=[user_email] )
                return Response({'detail':'Email Sent Successfully'})
            except Exception as e:
                return Response({'detail':f'Error in Sending email: {e}'})
        else:
            return Response({'detail':'All fields required'})
        
            

    # http_method_names =['post']

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            return Response({'detail':f'User with Email Does Not Exist..'}, status= status.HTTP_400_BAD_REQUEST)
        

        token = RefreshToken.for_user(user).access_token
        reset_url = f"{settings.FRONTEND_URL}/reset-pass/{token}"
        context =  {'reset_url':reset_url, 'user':UserSerializer(user).data}
        print(reset_url)
        subject ="password reset"
        message = render_to_string(
             template_name='email/password_reset_email.html',
             context= context
             )
        
        # message =f"Click link below to reset your password:\n {reset_url}"
        
        try:
            send_email = EmailMessage(subject= subject, body=message, from_email=settings.DEFAULT_FROM_EMAIL, to=[user.email])
            # send_email =EmailMessage(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.email])
            send_email.content_subtype = 'html'
            send_email.send()
            
        except Exception as e:
            return Response({"detail": f"Error in sending password reset..: {e}"}, status= status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail": f"Password  Reset link sent to your mail check it and verify it.message"}, status= status.HTTP_200_OK)
        
      
        
        # return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request,token):
        print("token: ",token)
        password = request.data.get('password')
        try:
            access_token = AccessToken(token= token)
            user_id = access_token["user_id"]
            user = User.objects.get(id = user_id)
        except Exception as e:
            return Response({"detail":f"Invalid or expired Token: {e}"}, status= status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save()
        return Response({'detail':"Password reset successfull"}, status= status.HTTP_200_OK)

   

# admin only view


class CustomerOnlyView(APIView):
    permission_classes= [AllowAny]



    def get(self, request):
        return Response({"message": "view for only customers"})


class SomeAdminOnlyView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({"message": "view for admins only..."})

#  for paytm

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
# from .serializers import PaymentSerializer
import paytmchecksum

import random
import string
import json
import requests

#  for paytm
class PaytmPaymentAPI(APIView):
    def post(self, request):
        # get the amount and customer info
        amount = request.data.get('total_price')
        cust_id = str(request.data.get('cust_id'))
        order_id = str(request.data.get('order_id'))
        #  prepare Paytm Parameters
        paytm_params= dict()
        paytm_params["body"] = {
            "requestType":"Payment",
            'mid': settings.PAYTM_MERCHANT_ID,
            'websiteName':settings.PAYTM_WEBSITE ,
            'orderId': str(order_id),
            'callbackUrl': settings.PAYTM_CALLBACK_URL,
            'txnAmount':{
                "value":str(amount),
                "current":"INR",
            },
            'userInfo': {
                "custId": str(cust_id),
            }
        }

        try:
        #  generate checksum using paytm library

            checksum = paytmchecksum.generateSignature(json.dumps(paytm_params["body"]), key=settings.PAYTM_MERCHANT_KEY)
        except Exception as e:
            return Response({"error": f"error generate check sum : {e}"}, status=status.HTTP_400_BAD_REQUEST)
        # add checksum to parameters
        paytm_params['head'] ={
            "signature" : checksum,
        } 
        post_data = json.dumps(paytm_params)
        url = f"https://securegw{settings.PAYTM_URL}.paytm.in/theia/api/v1/initiateTransaction?mid={settings.PAYTM_MERCHANT_ID}&order_Id={order_id}"
        print(url)
        response = requests.post(url, data = post_data, headers={"Content-type":"application/json"}).json()
        print(response)
        return Response(data= response,status= status.HTTP_200_OK)
    

class PaytmCallback(APIView):
    def post(self, request):
        # paytm sends response with transaction details
        order_id = request.data.get('order_id')
        paytmParams = dict()
        paytmParams["body"] = {
            "mid" : str(settings.PAYTM_MERCHANT_ID),
            "orderId": str(order_id)
        }
        check_sum = paytmchecksum.generateSignature(json.dumps(paytmParams['body']),key=settings.PAYTM_MERCHANT_KEY)
        # VERIFY CHECK SUM
        paytmParams['head']={
            'signature':check_sum
        }
        post_data = json.dumps(paytmParams)
        url= "https://securegw{settings.PAYTM_URL}.paytm.in/v3/order/status"
        response = requests.post(url=url, data=post_data, headers={"Content-Type":"application/json"}).json()

        return Response(data= response, status=status.HTTP_200_OK)

       
       
    
        