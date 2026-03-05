import pytest
from rest_framework import status
from apps.inventory.models import Category, Product
from apps.sales.models import Sale
from decimal import Decimal


@pytest.mark.django_db
class TestCustomers:

    def test_create_customer_with_valid_data(self, authenticated_client):
        response = authenticated_client.post(
            '/api/v1/users/customers/',
            {'name': 'María García', 'phone': '0991234567'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        customer = response.json()
        assert 'id' in customer or 'pk' in customer
        assert customer['name'] == 'María García'
        assert customer['phone'] == '0991234567'

    def test_create_customer_with_empty_name_gets_default(self, authenticated_client):
        response = authenticated_client.post(
            '/api/v1/users/customers/',
            {'phone': '0991234567'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        customer = response.json()
        assert customer['name'] == 'ANONIMO'

    def test_create_customer_with_empty_phone_gets_default(self, authenticated_client):
        response = authenticated_client.post(
            '/api/v1/users/customers/',
            {'name': 'Test Customer'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        customer = response.json()
        assert customer['phone'] == '000000000'

    def test_create_customer_strips_whitespace(self, authenticated_client):
        response = authenticated_client.post(
            '/api/v1/users/customers/',
            {'name': '  Juan Perez  ', 'phone': '  0991234567  '},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        customer = response.json()
        assert customer['name'] == 'Juan Perez'
        assert customer['phone'] == '0991234567'

    def test_list_customers(self, authenticated_client, test_customer):
        response = authenticated_client.get('/api/v1/users/customers/')
        assert response.status_code == status.HTTP_200_OK

    def test_filter_customers_by_phone(self, authenticated_client, test_customer):
        response = authenticated_client.get('/api/v1/users/customers/?phone=099')
        assert response.status_code == status.HTTP_200_OK
        results = response.json().get('results', response.json())
        assert len(results) > 0
        for customer in results:
            assert '099' in customer['phone']

    def test_update_customer_with_sales_fails(self, authenticated_client, test_customer, test_user):
        category = Category.objects.create(name='Test Category', is_active=True)
        product = Product.objects.create(
            name='Test Product',
            barcode='1234567890123',
            category=category,
            price=Decimal('10.00'),
            stock_quantity=100,
            is_active=True
        )
        Sale.objects.create(
            created_by=test_user,
            customer=test_customer,
            status='PAID',
            total_amount=Decimal('10.00')
        )

        response = authenticated_client.patch(
            f'/api/v1/users/customers/{test_customer.id}/',
            {'name': 'Nuevo Nombre'},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_customer_with_sales_fails(self, authenticated_client, test_customer, test_user):
        category = Category.objects.create(name='Test Category 2', is_active=True)
        product = Product.objects.create(
            name='Test Product 2',
            barcode='1234567890124',
            category=category,
            price=Decimal('10.00'),
            stock_quantity=100,
            is_active=True
        )
        Sale.objects.create(
            created_by=test_user,
            customer=test_customer,
            status='PAID',
            total_amount=Decimal('10.00')
        )

        response = authenticated_client.delete(f'/api/v1/users/customers/{test_customer.id}/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUsers:

    def test_list_users_with_valid_token(self, authenticated_client, test_user):
        response = authenticated_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
        assert isinstance(data['results'], list)
        for user in data['results']:
            assert 'id' in user
