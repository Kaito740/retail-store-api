import requests

BASE_URL = "http://localhost:8000//api/v1"
LOGIN_URL = f"{BASE_URL}/users/login/"
CATEGORIES_URL = f"{BASE_URL}/inventory/categories/"
PRODUCTS_URL = f"{BASE_URL}/inventory/products/"
CUSTOMERS_URL = f"{BASE_URL}/users/customers/"
SALES_URL = f"{BASE_URL}/sales/"

USERNAME = "testing"
PASSWORD = "testing123"
TIMEOUT = 30

def test_post_api_v1_sales_create_sale_with_insufficient_stock():
    # Authenticate and get token
    login_resp = requests.post(
        LOGIN_URL,
        json={"username": USERNAME, "password": PASSWORD},
        timeout=TIMEOUT,
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json().get("token")
    assert token, "No token received from login"

    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }

    category_id = None
    product_id = None
    customer_id = None

    # Create category
    try:
        cat_resp = requests.post(
            CATEGORIES_URL,
            json={"name": "Test Category"},
            headers=headers,
            timeout=TIMEOUT,
        )
        assert cat_resp.status_code == 201, f"Category creation failed: {cat_resp.text}"
        category_id = cat_resp.json().get("id")
        assert category_id is not None, "Category ID missing in response"

        # Create product with limited stock (e.g. stock=5)
        prod_resp = requests.post(
            PRODUCTS_URL,
            json={
                "name": "Test Product",
                "price": "10.00",
                "stock": 5,
                "category": category_id
            },
            headers=headers,
            timeout=TIMEOUT,
        )
        assert prod_resp.status_code == 201, f"Product creation failed: {prod_resp.text}"
        product_id = prod_resp.json().get("id")
        assert product_id is not None, "Product ID missing in response"

        # Create a customer (optional in sales, but good to have)
        cust_resp = requests.post(
            CUSTOMERS_URL,
            json={"name": "Test Customer", "phone": "1234567890"},
            headers=headers,
            timeout=TIMEOUT,
        )
        assert cust_resp.status_code == 201, f"Customer creation failed: {cust_resp.text}"
        customer_id = cust_resp.json().get("id")
        assert customer_id is not None, "Customer ID missing in response"

        # Attempt to create sale with quantity > stock (e.g., 10 > 5)
        sale_payload = {
            "customer": customer_id,
            "items": [
                {
                    "product": product_id,
                    "quantity": 10
                }
            ]
        }
        sale_resp = requests.post(
            SALES_URL,
            json=sale_payload,
            headers=headers,
            timeout=TIMEOUT,
        )
        assert sale_resp.status_code == 409, f"Expected 409 but got {sale_resp.status_code}"
        # Confirm 'Insufficient stock' error message in response
        error_resp = sale_resp.json()
        found_insufficient_stock = False
        if isinstance(error_resp, dict):
            # Could be error key or detail or non field errors
            # Check possible error messages for indication
            for v in error_resp.values():
                if isinstance(v, str) and "Insufficient stock" in v:
                    found_insufficient_stock = True
                    break
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, str) and "Insufficient stock" in item:
                            found_insufficient_stock = True
                            break
                if found_insufficient_stock:
                    break
        assert found_insufficient_stock, f"Expected 'Insufficient stock' error message but got {error_resp}"

    finally:
        # Cleanup: delete created sale is not created due to insufficient stock
        # Cleanup product
        if product_id is not None:
            requests.delete(f"{PRODUCTS_URL}{product_id}/", headers=headers, timeout=TIMEOUT)

        # Cleanup category
        if category_id is not None:
            requests.delete(f"{CATEGORIES_URL}{category_id}/", headers=headers, timeout=TIMEOUT)

        # Cleanup customer
        if customer_id is not None:
            requests.delete(f"{CUSTOMERS_URL}{customer_id}/", headers=headers, timeout=TIMEOUT)


test_post_api_v1_sales_create_sale_with_insufficient_stock()