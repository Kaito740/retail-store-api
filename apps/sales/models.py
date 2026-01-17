from django.db import models
from inventory.models import Product
from users.models import Customer
from django.conf import settings

# Create your models here.
class Sale(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft",
        CONFIRMED = "CONFIRMED", "Confirmed",
        PAID = "PAID", "Paid",
        CANCELLED = "CANCELLED", "Cancelled"
    status = models.CharField(max_length=10,choices=Status.choices,default=Status.DRAFT)
    total_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True,blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=10,decimal_places=2)
    subtotal = models.DecimalField(max_digits=10,decimal_places=2)