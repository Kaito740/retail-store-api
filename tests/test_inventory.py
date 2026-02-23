import pytest
from rest_framework import status
from apps.inventory.models import Category, Product
from decimal import Decimal


@pytest.mark.django_db
class TestCategories:

    def test_get_categories_with_valid_token(self, authenticated_client):
        response = authenticated_client.get('/api/v1/inventory/categories/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.json()

    def test_create_category_with_valid_data(self, authenticated_client):
        response = authenticated_client.post(
            '/api/v1/inventory/categories/',
            {'name': 'Toys'},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['name'] == 'Toys'
        assert 'id' in response.json()

    def test_create_category_without_name(self, authenticated_client):
        response = authenticated_client.post(
            '/api/v1/inventory/categories/',
            {},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProducts:

    def test_get_products_with_valid_token(self, authenticated_client):
        response = authenticated_client.get('/api/v1/inventory/products/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_product_with_valid_data(self, authenticated_client, active_category):
        response = authenticated_client.post(
            '/api/v1/inventory/products/',
            {
                'name': 'Test Product',
                'barcode': '1112223334445',
                'category': active_category.id,
                'price': '15.99',
                'stock_quantity': 50
            },
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['name'] == 'Test Product'
        assert response.json()['category'] == active_category.id

    def test_create_product_with_inactive_category_fails(self, authenticated_client, db):
        inactive_category = Category.objects.create(name='Inactive', is_active=False)
        response = authenticated_client.post(
            '/api/v1/inventory/products/',
            {
                'name': 'Test Product',
                'barcode': '1112223334446',
                'category': inactive_category.id,
                'price': '15.99',
                'stock_quantity': 50
            },
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_product_with_valid_category(self, authenticated_client, active_category):
        response = authenticated_client.post(
            '/api/v1/inventory/products/',
            {
                'name': 'TestProductTC007',
                'price': '19.99',
                'stock_quantity': 100,
                'barcode': '1112223334447',
                'category': active_category.id
            },
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        product_data = response.json()
        assert product_data['name'] == 'TestProductTC007'
        assert product_data['category'] == active_category.id
        assert str(product_data['price']) == '19.99'
        assert product_data['stock_quantity'] == 100

    def test_create_category_with_short_name_fails(self, authenticated_client):
        response = authenticated_client.post(
            '/api/v1/inventory/categories/',
            {'name': 'A'},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_product_with_negative_price_fails(self, authenticated_client, active_category):
        response = authenticated_client.post(
            '/api/v1/inventory/products/',
            {
                'name': 'Negative Price Product',
                'barcode': '1112223334448',
                'category': active_category.id,
                'price': '-10.00',
                'stock_quantity': 50
            },
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_product_with_inactive_product_fails(self, authenticated_client, active_category, db):
        inactive_product = Product.objects.create(
            name='Inactive Product',
            barcode='1112223334449',
            category=active_category,
            price=Decimal('10.00'),
            stock_quantity=50,
            is_active=False
        )
        response = authenticated_client.post(
            '/api/v1/sales/',
            {
                'customer': None,
                'items': [
                    {'product': inactive_product.id, 'quantity': 1}
                ]
            },
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
