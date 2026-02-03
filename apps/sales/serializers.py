from rest_framework.serializers import ModelSerializer
from .models import Sale, SaleItem

class SaleItemSerializer(ModelSerializer):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity']

class SaleSerializer(ModelSerializer):
    items = SaleItemSerializer(many=True)
    class Meta:
        model = Sale
        fields = ['status', 'customer', 'items']