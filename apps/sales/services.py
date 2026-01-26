from django.db import transaction
from apps.inventory.models import Product
from apps.users.models import Customer
from .models import Sale, SaleItem
from django.core.exceptions import ValidationError
from decimal import Decimal

def _verify_products(product_id, quantity_requested):
    product_data = Product.objects.filter(id=product_id).first()
    if not product_data:
        raise ValidationError('El producto no fue encontrado.')
    if product_data.stock_quantity < quantity_requested:
        raise ValidationError(f'Stock insuficiente para: {product_data.name}. '
                              f'Disponible: {product_data.stock_quantity}')
    return product_data

def _calculate_subtotal(quantity, unit_price):
    subTotal = Decimal(quantity)  * Decimal(unit_price)
    return subTotal

def sale_paid(*, created_by, products_data, customer=None):
    with transaction.atomic():
        sale = Sale.objects.create(
            created_by=created_by,
            customer=customer,
            status=Sale.Status.PAID
        )
        accumulated_total = Decimal('0.00')
        
        for item in products_data:
            product = _verify_products(item['product_id'], item['quantity'])
            current_subtotal = _calculate_subtotal(item['quantity'], product.price)
            product.stock_quantity -= item['quantity']
            product.save(update_fields=['stock_quantity'])
            
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=item['quantity'],
                unit_price=product.price,
                subtotal=current_subtotal
            )

            accumulated_total += current_subtotal

        sale.total_amount = accumulated_total
        sale.save() 

    return sale

def sale_cancelled(*, sale_id):
    sale_data = Sale.objects.filter(id=sale_id).first()
    if not sale_data:
        raise ValidationError('Venta no encontrada')
    
    if sale_data.status == Sale.Status.CANCELLED:
        raise ValidationError('Esta venta ya fue cancelada')

    with transaction.atomic(): 
        items_venta = SaleItem.objects.filter(sale=sale_data)
        
        for item in items_venta:
            product = item.product 
            product.stock_quantity += item.quantity
            product.save(update_fields=['stock_quantity'])

        sale_data.status = Sale.Status.CANCELLED
        sale_data.save(update_fields=['status'])
        
    return sale_data