from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from .views import ProductViewSet, CartViewSet, OrderViewSet,RegisterAPIView,LoginAPIView,ContactApiView, PasswordResetRequestView, PasswordResetConfirmView
from rest_framework_simplejwt import views as jwt_views
from .views import PaytmCallback, PaytmPaymentAPI
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'cart', CartViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('auth/register/',RegisterAPIView.as_view(), name='register'),
    path('auth/login/',LoginAPIView.as_view(), name= 'login'),
    # path('token', jwt_views.TokenObtainPairView.as_view(), name= 'token_obtain_pair'),
    # path('token/refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/',PasswordResetRequestView.as_view(), name="password-reset-request"),
    path('password-reset/<str:token>/', PasswordResetConfirmView.as_view(), name="password-reset"),
    path('auth/contact/',ContactApiView.as_view(), name='contact'),
    # paytm
    path('payment/',PaytmPaymentAPI.as_view(), name='payment-initiate'),
    path('payment/callback/', PaytmCallback.as_view(), name='payment-callback'),
    path('',include(router.urls)),
    # path('checkout/',CustomerOnlyView.as_view(), name='customer'),
   
]



