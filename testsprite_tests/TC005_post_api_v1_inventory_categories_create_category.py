import requests

BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "testing"
PASSWORD = "testing123"
TIMEOUT = 30

def test_post_api_v1_inventory_categories_create_category():
    # Step 1: Login to get token
    login_url = f"{BASE_URL}/users/login/"
    login_payload = {"username": USERNAME, "password": PASSWORD}
    login_headers = {"Content-Type": "application/json"}
    response = requests.post(login_url, json=login_payload, headers=login_headers, timeout=TIMEOUT)
    assert response.status_code == 200, f"Login failed with status {response.status_code}"
    token = response.json().get("token")
    assert token and isinstance(token, str), "No token received from login"

    # Step 2: Create a new category with valid data and valid token
    category_url = f"{BASE_URL}/inventory/categories/"
    category_payload = {"name": "Beverages", "description": "Drinks and refreshments"}
    category_headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    try:
        create_response = requests.post(category_url, json=category_payload, headers=category_headers, timeout=TIMEOUT)
        assert create_response.status_code == 201, f"Category creation failed with status {create_response.status_code}"
        category_data = create_response.json()
        assert "id" in category_data and isinstance(category_data["id"], int), "Category id missing or invalid"
        assert category_data.get("name") == category_payload["name"], "Category name mismatch"
        # description is optional, but if returned check consistency
        if "description" in category_data:
            assert category_data["description"] == category_payload["description"], "Category description mismatch"
    finally:
        # Cleanup: delete the created category if exists
        if 'category_data' in locals() and "id" in category_data:
            category_id = category_data["id"]
            delete_url = f"{category_url}{category_id}/"
            requests.delete(delete_url, headers=category_headers, timeout=TIMEOUT)

test_post_api_v1_inventory_categories_create_category()