from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import Category, Product

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','is_active']
        read_only_fields = ['id']

class ProductSerializer(ModelSerializer):
    category = PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = Product
        fields = ['id','name','barcode','category','price','stock_quantity','is_active']
        read_only_fields = ['id']