from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, ValidationError
from .models import Sale, SaleItem
from apps.users.models import Customer

class SaleItemSerializer(ModelSerializer):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity']

    def validate_product(self, value):
        if not value.is_active:
            raise ValidationError('El producto debe estar activo para poder venderlo.')
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise ValidationError('La cantidad debe ser mayor a 0.')
        return value

class SaleItemReadSerializer(ModelSerializer):
    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'subtotal']

class SaleSerializer(ModelSerializer):
    items = SaleItemSerializer(many=True)
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Sale
        fields = ['customer', 'items']

    def validate_customer(self, value):
        if value == '' or value is None:
            return None
        return value

class SaleReadSerializer(ModelSerializer):
    items = SaleItemReadSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'status', 'total_amount', 'customer', 'customer_name', 'created_by', 'created_by_username', 'created_at', 'items']