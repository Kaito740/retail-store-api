import requests

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/users/login/"
SALES_URL = f"{BASE_URL}/sales/"
PRODUCTS_URL = f"{BASE_URL}/inventory/products/"
CATEGORIES_URL = f"{BASE_URL}/inventory/categories/"

USERNAME = "testing"
PASSWORD = "testing123"
TIMEOUT = 30

def login_get_token(username, password):
    resp = requests.post(
        LOGIN_URL,
        json={"username": username, "password": password},
        timeout=TIMEOUT
    )
    resp.raise_for_status()
    token = resp.json().get("token")
    assert token and isinstance(token, str)
    return token

def create_category(token, name="Test Category"):
    headers = {"Authorization": f"Token {token}"}
    data = {"name": name}
    resp = requests.post(CATEGORIES_URL, json=data, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    category = resp.json()
    assert category.get("id")
    return category

def create_product(token, category_id, name="Test Product", price="9.99", stock=10):
    headers = {"Authorization": f"Token {token}"}
    data = {
        "name": name,
        "price": price,
        "stock": stock,
        "category": category_id
    }
    resp = requests.post(PRODUCTS_URL, json=data, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    product = resp.json()
    assert product.get("id")
    return product

def create_sale(token, product_id, quantity):
    headers = {"Authorization": f"Token {token}"}
    data = {
        "items": [
            {"product": product_id, "quantity": quantity}
        ]
    }
    resp = requests.post(SALES_URL, json=data, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    sale = resp.json()
    assert sale.get("id")
    return sale

def get_product(token, product_id):
    headers = {"Authorization": f"Token {token}"}
    resp = requests.get(f"{PRODUCTS_URL}{product_id}/", headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def get_sale(token, sale_id):
    headers = {"Authorization": f"Token {token}"}
    resp = requests.get(f"{SALES_URL}{sale_id}/", headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def patch_sale_cancel(token, sale_id):
    headers = {"Authorization": f"Token {token}"}
    data = {"action": "cancel"}
    resp = requests.patch(f"{SALES_URL}{sale_id}/", json=data, headers=headers, timeout=TIMEOUT)
    return resp

def test_patch_api_v1_sales_cancel_sale():
    token = login_get_token(USERNAME, PASSWORD)
    headers = {"Authorization": f"Token {token}"}

    # Setup: Create category, product, and sale
    category = create_category(token, name="Beverages")
    product = create_product(token, category_id=category["id"], name="Coffee", price="3.50", stock=10)

    # Create a sale with quantity 2
    sale = None
    try:
        sale = create_sale(token, product_id=product["id"], quantity=2)

        # Check product stock after sale - should be reduced by 2
        product_after_sale = get_product(token, product["id"])
        expected_stock_after_sale = product["stock"] - 2
        assert product_after_sale["stock"] == expected_stock_after_sale or product_after_sale["stock"] == (product.get("stock",10) - 2)

        # Cancel the sale
        resp = patch_sale_cancel(token, sale["id"])
        assert resp.status_code == 200
        cancelled_sale = resp.json()
        assert cancelled_sale.get("state") == "CANCELLED"

        # Check product stock restored
        product_after_cancel = get_product(token, product["id"])
        assert product_after_cancel["stock"] == product["stock"]

    finally:
        # Cleanup: Attempt to delete sale if possible (no DELETE endpoint described)
        # Attempt to cancel again to avoid leaving a pending sale
        if sale:
            # If sale not cancelled, try cancelling again
            try:
                patch_sale_cancel(token, sale["id"])
            except:
                pass
        # Attempt to delete product and category if endpoints supported (not described)
        # So no deletion performed.
        pass

test_patch_api_v1_sales_cancel_sale()
