from rest_framework.serializers import ModelSerializer
from .models import Category

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','is_active']
        read_only_fields = ['id']