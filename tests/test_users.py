import pytest
from rest_framework import status


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
