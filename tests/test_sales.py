import pytest
from rest_framework import status
from apps.inventory.models import Product
from apps.users.models import Customer
from apps.sales.models import Sale
from decimal import Decimal


@pytest.mark.django_db
class TestSales:

    def test_create_sale_with_valid_data(self, authenticated_client, active_category, test_customer):
        product = Product.objects.create(
            name='Sale Test Product',
            barcode='9998887776661',
            category=active_category,
            price=Decimal('20.00'),
            stock_quantity=10,
            is_active=True
        )

        response = authenticated_client.post(
            '/api/v1/sales/',
            {
                'customer': test_customer.id,
                'items': [
                    {'product': product.id, 'quantity': 3}
                ]
            },
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        sale_data = response.json()
        assert 'sale_id' in sale_data or 'id' in sale_data
        assert sale_data.get('status') == 'PAID'
        assert 'total_amount' in sale_data

        product.refresh_from_db()
        assert product.stock_quantity == 7

    def test_cancel_sale_and_restore_stock(self, authenticated_client, active_category, test_customer):
        product = Product.objects.create(
            name='Cancel Test Product',
            barcode='9998887776662',
            category=active_category,
            price=Decimal('10.00'),
            stock_quantity=5,
            is_active=True
        )
        initial_stock = product.stock_quantity

        sale_response = authenticated_client.post(
            '/api/v1/sales/',
            {
                'customer': test_customer.id,
                'items': [
                    {'product': product.id, 'quantity': 1}
                ]
            },
            format='json'
        )
        assert sale_response.status_code == status.HTTP_201_CREATED
        sale_id = sale_response.json().get('sale_id')

        product.refresh_from_db()
        assert product.stock_quantity == initial_stock - 1

        cancel_response = authenticated_client.patch(
            f'/api/v1/sales/{sale_id}/',
            {'action': 'cancel'},
            format='json'
        )
        assert cancel_response.status_code == status.HTTP_200_OK
        assert cancel_response.json().get('status') == 'CANCELLED'

        product.refresh_from_db()
        assert product.stock_quantity == initial_stock

    def test_get_sale_details(self, authenticated_client, active_category, test_customer):
        product = Product.objects.create(
            name='Detail Test Product',
            barcode='9998887776663',
            category=active_category,
            price=Decimal('15.00'),
            stock_quantity=10,
            is_active=True
        )

        sale_response = authenticated_client.post(
            '/api/v1/sales/',
            {
                'customer': test_customer.id,
                'items': [
                    {'product': product.id, 'quantity': 2}
                ]
            },
            format='json'
        )
        sale_id = sale_response.json().get('sale_id')

        detail_response = authenticated_client.get(f'/api/v1/sales/{sale_id}/')
        assert detail_response.status_code == status.HTTP_200_OK
        sale_detail = detail_response.json()
        assert sale_detail.get('status') == 'PAID'
        assert len(sale_detail.get('items', [])) > 0

    def test_create_sale_with_insufficient_stock_fails(self, authenticated_client, active_category, test_customer):
        product = Product.objects.create(
            name='Insufficient Stock Product',
            barcode='9998887776664',
            category=active_category,
            price=Decimal('10.00'),
            stock_quantity=2,
            is_active=True
        )
        initial_stock = product.stock_quantity

        response = authenticated_client.post(
            '/api/v1/sales/',
            {
                'customer': test_customer.id,
                'items': [
                    {'product': product.id, 'quantity': 10}
                ]
            },
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        product.refresh_from_db()
        assert product.stock_quantity == initial_stock

    def test_filter_sales_by_status(self, authenticated_client, active_category, test_customer):
        product = Product.objects.create(
            name='Filter Test Product',
            barcode='9998887776665',
            category=active_category,
            price=Decimal('10.00'),
            stock_quantity=10,
            is_active=True
        )

        authenticated_client.post(
            '/api/v1/sales/',
            {
                'customer': test_customer.id,
                'items': [
                    {'product': product.id, 'quantity': 1}
                ]
            },
            format='json'
        )

        response = authenticated_client.get('/api/v1/sales/?status=PAID')
        assert response.status_code == status.HTTP_200_OK
        results = response.json().get('results', response.json())
        assert len(results) > 0
        for sale in results:
            assert sale.get('status') == 'PAID'

    def test_cancel_already_cancelled_sale_fails(self, authenticated_client, active_category, test_customer):
        product = Product.objects.create(
            name='Cancel Twice Product',
            barcode='9998887776666',
            category=active_category,
            price=Decimal('10.00'),
            stock_quantity=5,
            is_active=True
        )
        initial_stock = product.stock_quantity

        sale_response = authenticated_client.post(
            '/api/v1/sales/',
            {
                'customer': test_customer.id,
                'items': [
                    {'product': product.id, 'quantity': 1}
                ]
            },
            format='json'
        )
        sale_id = sale_response.json().get('sale_id')

        cancel_response = authenticated_client.patch(
            f'/api/v1/sales/{sale_id}/',
            {'action': 'cancel'},
            format='json'
        )
        assert cancel_response.status_code == status.HTTP_200_OK

        cancel_again_response = authenticated_client.patch(
            f'/api/v1/sales/{sale_id}/',
            {'action': 'cancel'},
            format='json'
        )
        assert cancel_again_response.status_code == status.HTTP_400_BAD_REQUEST

        product.refresh_from_db()
        assert product.stock_quantity == initial_stock

    def test_create_sale_without_customer(self, authenticated_client, active_category):
        product = Product.objects.create(
            name='No Customer Product',
            barcode='9998887776667',
            category=active_category,
            price=Decimal('10.00'),
            stock_quantity=10,
            is_active=True
        )

        response = authenticated_client.post(
            '/api/v1/sales/',
            {
                'items': [
                    {'product': product.id, 'quantity': 1}
                ]
            },
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        sale = Sale.objects.get(id=response.json().get('sale_id'))
        assert sale.customer.name == 'ANONIMO'
