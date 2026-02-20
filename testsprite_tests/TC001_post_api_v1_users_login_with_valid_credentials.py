import requests

def test_post_api_v1_users_login_with_valid_credentials():
    base_url = "http://localhost:8000/api/v1"
    login_url = f"{base_url}/users/login/"

    payload = {
        "username": "testing",
        "password": "testing123"
    }

    try:
        response = requests.post(login_url, json=payload, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    json_data = response.json()
    assert "token" in json_data, "Login response JSON should contain 'token'"
    assert isinstance(json_data["token"], str) and len(json_data["token"]) > 0, "Token should be a non-empty string"


test_post_api_v1_users_login_with_valid_credentials()