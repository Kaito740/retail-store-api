from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=70, validators=[MinLengthValidator(2,message='El nombre de la categoria es muy corto.')] ,unique=True)
    is_active = models.BooleanField(default=False)
        
    def save(self,*args,**kwargs):
        self.full_clean()
        super().save(*args,**kwargs)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=70, validators=[MinLengthValidator(2,message='El nombre del producto es muy corto.')])
    barcode = models.CharField(max_length=70,unique=True)
    category = models.ForeignKey(Category,on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=8,decimal_places=2,validators=[MinValueValidator(0.00,message='El precio no puede ser negativo.')])
    stock_quantity = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=False)
    
    def save(self,*args,**kwargs):
        self.full_clean()
        super().save(*args,**kwargs)
    
    def __str__(self):
        return self.name