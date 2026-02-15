from django.db import models
from apps.inventory.models import Product
from apps.users.models import Customer
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

# Create your models here.
class Sale(models.Model):
    class Status(models.TextChoices):
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    status = models.CharField(max_length=10, choices=Status.choices)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0.00, message='El monto total no debe ser menor a 0.')])
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "venta"
        verbose_name_plural = "ventas"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['customer']),
            models.Index(fields=['created_by']),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Venta #{self.id} - {self.status} - ${self.total_amount}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "ítem de venta"
        verbose_name_plural = "ítems de venta"
        ordering = ['id']
        indexes = [
            models.Index(fields=['sale']),
            models.Index(fields=['product']),
        ]

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'La cantidad no debe ser 0.'})
        if self.unit_price <= 0:
            raise ValidationError({'unit_price': 'El precio unitario no debe ser 0 o negativo.'})

        temp_subtotal = self.quantity * self.unit_price
        if temp_subtotal <= 0:
            raise ValidationError('El subtotal calculado no es valido.')

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x{self.quantity} = ${self.subtotal}"