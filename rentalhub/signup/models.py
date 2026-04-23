from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta

class UserInfo(AbstractUser):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]

    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)



    
    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Electronics', 'Electronics'),
        ('Furniture', 'Furniture'),
        ('Vehicles', 'Vehicles'),
        ('Clothing', 'Clothing'),
        ('Books', 'Books'),
        # Add more categories as needed
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.name

class CartItem(models.Model):
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rental_days = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField(blank=True, null=True)

    def total_price(self):
        return self.product.price_per_day * self.rental_days

class Rental(models.Model):
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rental_days = models.PositiveIntegerField()
    rented_at = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField(max_length=255, default="Not provided")

    @property
    def return_date(self):
        return self.rented_at + timedelta(days=self.rental_days)

    @property
    def time_left(self):
        now = timezone.now()
        remaining = self.return_date - now
        if remaining.total_seconds() > 0:
            return remaining
        return timedelta(0)  # already expired

    def _str_(self):
        return f"{self.user.username} rented {self.product.name}"