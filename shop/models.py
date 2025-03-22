from django.db import models
from django.contrib.auth.models import User 
from datetime import timezone
import uuid
class Product(models.Model):
    # name = models.CharField(max_length= 255, default="name")
    title = models.CharField(max_length= 255, default="")
    image = models.URLField(default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(default="")

    brand = models.CharField(max_length= 50, default="")
    model = models.CharField(max_length= 50, default="")
    color = models.CharField(max_length= 50, default="")
    category = models.CharField(max_length= 50, default="")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default= 0)

    stock = models.IntegerField(default= 0)
    rating = models.DecimalField(max_digits=2,decimal_places=2,default= 0)

    def __str__(self):
        return self.title

class Cart(models.Model):

    product = models.ForeignKey(Product , related_name='carts' ,on_delete= models.CASCADE, default="")
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.id}'s Cart with {self.quantity}"
    
class Delivery(models.Model):
    fname = models.CharField(max_length= 50, default="")
    lname = models.CharField(max_length= 50 , default="")
    email = models.EmailField(max_length= 50, default="")
    mobileno = models.CharField(max_length= 10,default="")
    address = models.CharField(max_length=255, default="")
    country = models.CharField(max_length=50,default="")
    state = models.CharField(max_length=50, default="")
    city = models.CharField(max_length=50, default="")
    zip = models.CharField(max_length= 50, default="")
    
    def __str__(self):
        return f"{self.email} with {self.address}"
    
class Order(models.Model):
    # id = models.UUIDField(primary_key= True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name="orders", on_delete= models.CASCADE, default="")
    cart = models.ManyToManyField(Cart, related_name='orders', default="")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    delivery_detail = models.ForeignKey(Delivery, on_delete=models.CASCADE, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length= 50, default='pending')
    

    def __str__(self):
        return f"Order {self.id} by {self.total_price}"
    

    


    
    


