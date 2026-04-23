from django.contrib import admin
from .models import Product

# Register your models here.

admin.site.register(Product)

from django.contrib import admin
from .models import UserInfo, Product, Rental

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rental_days', 'delivery_address', 'rented_at')
    list_filter = ('rented_at', 'product')
    search_fields = ('user_username', 'product_name', 'delivery_address')