import requests

BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "testing"
PASSWORD = "testing123"
TIMEOUT = 30

def test_post_api_v1_sales_create_sale_with_sufficient_stock():
    session = requests.Session()
    try:
        # 1. Authenticate and get token
        login_resp = session.post(
            f"{BASE_URL}/users/login/",
            json={"username": USERNAME, "password": PASSWORD},
            timeout=TIMEOUT
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json().get("token")
        assert token, "No token received"

        headers = {"Authorization": f"Token {token}"}

        # 2. Create a category
        category_resp = session.post(
            f"{BASE_URL}/inventory/categories/",
            headers=headers,
            json={"name": "TestCategory"},
            timeout=TIMEOUT
        )
        assert category_resp.status_code == 201, f"Category creation failed: {category_resp.text}"
        category_id = category_resp.json().get("id")
        assert category_id is not None, "Category ID not returned"

        # 3. Create 2 products with sufficient stock
        products = []
        for prod_data in [
            {"name": "TestProduct1", "price": "10.00", "stock": 5, "category": category_id},
            {"name": "TestProduct2", "price": "20.00", "stock": 3, "category": category_id},
        ]:
            prod_resp = session.post(
                f"{BASE_URL}/inventory/products/",
                headers=headers,
                json=prod_data,
                timeout=TIMEOUT
            )
            assert prod_resp.status_code == 201, f"Product creation failed: {prod_resp.text}"
            product = prod_resp.json()
            products.append(product)

        # 4. Create a customer (optional)
        customer_resp = session.post(
            f"{BASE_URL}/users/customers/",
            headers=headers,
            json={"name": "Test Customer"},
            timeout=TIMEOUT
        )
        assert customer_resp.status_code == 201, f"Customer creation failed: {customer_resp.text}"
        customer_id = customer_resp.json().get("id")
        assert customer_id is not None, "Customer ID not returned"

        # 5. Create sale with items having quantity less than or equal to stock
        sale_items = [
            {"product": products[0]["id"], "quantity": 2},
            {"product": products[1]["id"], "quantity": 1},
        ]
        sale_payload = {"customer": customer_id, "items": sale_items}
        sale_resp = session.post(
            f"{BASE_URL}/sales/",
            headers=headers,
            json=sale_payload,
            timeout=TIMEOUT
        )
        assert sale_resp.status_code == 201, f"Sale creation failed: {sale_resp.text}"
        sale_data = sale_resp.json()
        sale_id = sale_data.get("id")
        assert sale_id is not None, "Sale ID not returned"
        assert "items" in sale_data, "Sale items missing in response"
        assert len(sale_data["items"]) == 2, "Sale items count mismatch"

        # 6. Verify that stock was decremented atomically
        # Fetch products again to check stock
        for ordered_item in sale_items:
            prod_id = ordered_item["product"]
            qty_ordered = ordered_item["quantity"]
            prod_resp_check = session.get(
                f"{BASE_URL}/inventory/products/",
                headers=headers,
                timeout=TIMEOUT
            )
            assert prod_resp_check.status_code == 200, f"Product list fetch failed: {prod_resp_check.text}"
            products_list = prod_resp_check.json()
            product = next((p for p in products_list if p["id"] == prod_id), None)
            assert product is not None, f"Product not found after sale: {prod_id}"
            # Original stock - qty ordered should equal current stock
            original_stock = next(p for p in products if p["id"] == prod_id)["stock"]
            expected_stock = original_stock - qty_ordered
            actual_stock = product["stock"]
            assert actual_stock == expected_stock, f"Stock mismatch for product {prod_id}: expected {expected_stock}, got {actual_stock}"

    finally:
        # Cleanup: delete the created sale, products, category, customer if deletion endpoints exist
        # Since no DELETE endpoints documented for sales/products/customers/categories,
        # We try best effort cleanup if endpoints existed:

        # Delete sale
        if 'sale_id' in locals():
            try:
                session.delete(f"{BASE_URL}/sales/{sale_id}/", headers=headers, timeout=TIMEOUT)
            except Exception:
                pass
        # Delete products
        if 'products' in locals():
            for p in products:
                try:
                    session.delete(f"{BASE_URL}/inventory/products/{p['id']}/", headers=headers, timeout=TIMEOUT)
                except Exception:
                    pass
        # Delete category
        if 'category_id' in locals():
            try:
                session.delete(f"{BASE_URL}/inventory/categories/{category_id}/", headers=headers, timeout=TIMEOUT)
            except Exception:
                pass
        # Delete customer
        if 'customer_id' in locals():
            try:
                session.delete(f"{BASE_URL}/users/customers/{customer_id}/", headers=headers, timeout=TIMEOUT)
            except Exception:
                pass

test_post_api_v1_sales_create_sale_with_sufficient_stock()
