from django.contrib import admin
from .models import Product, Order, Cart, Delivery

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Delivery)
