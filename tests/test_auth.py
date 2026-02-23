import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token


@pytest.mark.django_db
class TestAuthentication:

    def test_login_with_valid_credentials(self, api_client, test_user):
        response = api_client.post('/api/v1/users/login/', {
            'username': 'testing',
            'password': 'testing123'
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.json()
        assert isinstance(response.json()['token'], str)
        assert response.json()['token']
        assert 'user' in response.json()
        assert isinstance(response.json()['user'], dict)

    def test_login_with_missing_credentials(self, api_client, test_user):
        test_payloads = [
            {},
            {'username': 'testing'},
            {'password': 'testing123'}
        ]

        for payload in test_payloads:
            response = api_client.post('/api/v1/users/login/', payload, format='json')
            assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Failed for payload: {payload}"

    def test_login_with_invalid_credentials(self, api_client, test_user):
        response = api_client.post('/api/v1/users/login/', {
            'username': 'invalid_user',
            'password': 'wrong_password'
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.json()

    def test_logout_with_valid_token(self, api_client, test_user):
        token, _ = Token.objects.get_or_create(user=test_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = api_client.post('/api/v1/users/logout/')

        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.json()

    def test_logout_without_authorization_header(self, api_client):
        response = api_client.post('/api/v1/users/logout/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
