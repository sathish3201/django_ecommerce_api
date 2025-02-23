from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from .views import ProductViewSet, CartViewSet, OrderViewSet,RegisterAPIView,LoginAPIView,CustomerOnlyView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'cart', CartViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('auth/register/',RegisterAPIView.as_view(), name='register'),
    path('auth/login/',LoginAPIView.as_view(), name= 'login'),
    path('',include(router.urls)),
    # path('checkout/',CustomerOnlyView.as_view(), name='customer'),
   
]