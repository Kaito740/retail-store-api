import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apps.inventory.models import Category, Product
from apps.users.models import Customer
from decimal import Decimal


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    user, created = User.objects.get_or_create(
        username='testing',
        defaults={'email': 'testing@test.com'}
    )
    if created:
        user.set_password('testing123')
        user.save()
    return user


@pytest.fixture
def authenticated_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def active_category(db):
    category = Category.objects.create(name='Test Category', is_active=True)
    yield category
    from apps.sales.models import SaleItem
    products = Product.objects.filter(category=category)
    SaleItem.objects.filter(product__in=products).delete()
    products.delete()
    category.delete()


@pytest.fixture
def active_product(db, active_category):
    product = Product.objects.create(
        name='Test Product',
        barcode='1234567890123',
        category=active_category,
        price=Decimal('10.00'),
        stock_quantity=50,
        is_active=True
    )
    yield product
    product.delete()


@pytest.fixture
def test_customer(db):
    customer = Customer.objects.create(name='Test Customer', phone='0991234567')
    yield customer
    customer.delete()
