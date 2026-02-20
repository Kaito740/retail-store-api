import requests

BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/users/login/"
CATEGORY_URL = f"{BASE_URL}/inventory/categories/"
PRODUCT_URL = f"{BASE_URL}/inventory/products/"
TIMEOUT = 30

USERNAME = "testing"
PASSWORD = "testing123"


def test_post_api_v1_inventory_products_create_product_with_valid_data():
    # Authenticate and get token
    try:
        login_resp = requests.post(
            LOGIN_URL,
            json={"username": USERNAME, "password": PASSWORD},
            timeout=TIMEOUT,
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json().get("token")
        assert token and isinstance(token, str), "Token not found in login response"
        headers = {"Authorization": f"Token {token}"}

        # Create a category first (required for product)
        category_data = {"name": "Test Category for Product"}
        category_resp = requests.post(
            CATEGORY_URL, json=category_data, headers=headers, timeout=TIMEOUT
        )
        assert category_resp.status_code == 201, f"Category creation failed: {category_resp.text}"
        category = category_resp.json()
        category_id = category.get("id")
        assert category_id is not None, "Category ID missing in response"

        # Create product with valid data
        product_data = {
            "name": "Test Product",
            "description": "A test product description",
            "price": "9.99",
            "stock": 100,
            "category": category_id
        }
        product_resp = requests.post(
            PRODUCT_URL, json=product_data, headers=headers, timeout=TIMEOUT
        )
        assert product_resp.status_code == 201, f"Product creation failed: {product_resp.text}"
        product = product_resp.json()
        # Check response contains expected fields
        assert product.get("name") == product_data["name"], "Product name mismatch"
        assert product.get("description") == product_data["description"], "Product description mismatch"
        assert str(product.get("price")) == product_data["price"], "Product price mismatch"
        assert product.get("stock") == product_data["stock"], "Product stock mismatch"
        assert product.get("category") == category_id, "Product category mismatch"

    finally:
        # Cleanup: delete the created product and category if exist
        if 'product' in locals() and product.get("id"):
            try:
                requests.delete(
                    f"{PRODUCT_URL}{product['id']}/", headers=headers, timeout=TIMEOUT
                )
            except Exception:
                pass
        if 'category' in locals() and category.get("id"):
            try:
                requests.delete(
                    f"{CATEGORY_URL}{category['id']}/", headers=headers, timeout=TIMEOUT
                )
            except Exception:
                pass


test_post_api_v1_inventory_products_create_product_with_valid_data()