from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, ValidationError
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

    def validate_category(self, value):
        if not value.is_active:
            raise ValidationError('La categoría debe estar activa para crear un producto.')
        return value