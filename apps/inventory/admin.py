from django.contrib import admin
from .models import Category, Product
# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','barcode', 'category','price', 'stock_quantity', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name','barcode']
    list_editable = ['stock_quantity']

