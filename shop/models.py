from django.db import models
from django.contrib.auth.models import User 
from datetime import timezone

class Product(models.Model):
    # name = models.CharField(max_length= 255, default="name")
    title = models.CharField(max_length= 50, default="title")
    description = models.TextField(default=f"this is {title}")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.IntegerField(default= 0)
   
    discountPercentage = models.DecimalField(max_digits=10, decimal_places=2, default= 0.00)
    rating = models.IntegerField(default= 0)
    brand = models.CharField(max_length= 50, default="brand")
    category = models.CharField(max_length= 50, default="category")
    thumbnail = models.URLField(default="")
    images = []
    deleted = models.BooleanField(default= True)
    def __str__(self):
        return self.title

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username}'s Cart with {self.product.id}"
    
    def total_price(self):
        return self.product.price*self.quantity
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length= 50, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    
   
    
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete= models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.title} in Order {self.order.id}"
    
    def total_price(self):
        return self.product.price * self.quantity

