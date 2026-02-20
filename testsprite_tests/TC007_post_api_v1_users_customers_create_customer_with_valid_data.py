import requests

BASE_URL = "http://localhost:8000//api/v1/"
LOGIN_URL = BASE_URL + "users/login/"
CUSTOMERS_URL = BASE_URL + "users/customers/"
TIMEOUT = 30

USERNAME = "testing"
PASSWORD = "testing123"


def test_post_api_v1_users_customers_create_customer_with_valid_data():
    # Step 1: Login to get the token
    login_payload = {
        "username": USERNAME,
        "password": PASSWORD
    }
    login_resp = requests.post(
        LOGIN_URL,
        json=login_payload,
        timeout=TIMEOUT,
    )
    assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code} and body {login_resp.text}"
    token = login_resp.json().get("token")
    assert token and isinstance(token, str), "Token not found or invalid in login response"

    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }

    # Step 2: Create a customer with valid data
    customer_payload = {
        "name": "ACME Ltd",
        "phone": "099123456"
    }

    create_resp = requests.post(
        CUSTOMERS_URL,
        json=customer_payload,
        headers=headers,
        timeout=TIMEOUT,
    )

    try:
        assert create_resp.status_code == 201, f"Expected 201 Created, got {create_resp.status_code} with body {create_resp.text}"
        customer = create_resp.json()
        # Validate returned customer object contents
        assert "id" in customer and isinstance(customer["id"], int), "Customer ID missing or invalid"
        assert customer.get("name") == customer_payload["name"], f"Expected name '{customer_payload['name']}', got '{customer.get('name')}'"
        # Phone is optional in PRD but we sent it, so should match
        assert customer.get("phone") == customer_payload["phone"], f"Expected phone '{customer_payload['phone']}', got '{customer.get('phone')}'"
        # Email was not provided, so response may omit or be null
    finally:
        # Cleanup: delete the created customer to keep test isolated
        if create_resp.status_code == 201:
            customer_id = customer.get("id")
            if customer_id:
                del_resp = requests.delete(
                    f"{CUSTOMERS_URL}{customer_id}/",
                    headers=headers,
                    timeout=TIMEOUT,
                )
                # Optionally assert delete success or ignore if not implemented
                assert del_resp.status_code in (204, 200, 202), f"Failed to delete customer with id {customer_id}"

test_post_api_v1_users_customers_create_customer_with_valid_data()