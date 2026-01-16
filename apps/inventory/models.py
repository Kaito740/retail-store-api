from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=70, unique=True)
    is_active = models.BooleanField(default=False)

class Product(models.Model):
    name = models.CharField(max_length=70)
    barcoder = models.CharField(max_length=70,unique=True)
    category = models.ForeignKey(Category,on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    stock_quantity = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=False)

    """inventario: product y category
ventas: sale y saleitem
usuarios: customer and user(staff)"""