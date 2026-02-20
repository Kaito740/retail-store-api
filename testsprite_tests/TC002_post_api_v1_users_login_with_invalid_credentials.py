import requests

BASE_URL = "http://localhost:8000//api/v1/"
LOGIN_URL = BASE_URL + "users/login/"
TIMEOUT = 30


def test_post_api_v1_users_login_with_invalid_credentials():
    invalid_payload = {
        "username": "wronguser",
        "password": "wrongpassword"
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(LOGIN_URL, json=invalid_payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to login endpoint failed: {e}"

    assert response.status_code == 400, f"Expected status code 400 but got {response.status_code}"
    try:
        resp_json = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # According to PRD response schema for 400: 'Invalid credentials' error message expected
    # It might be in response text or in a json error message - check both
    # We'll check if the string 'Invalid credentials' appears either in JSON values or response text
    error_found = False
    if isinstance(resp_json, dict):
        for v in resp_json.values():
            if isinstance(v, str) and "Invalid credentials" in v:
                error_found = True
                break
    if not error_found:
        if "Invalid credentials" in response.text:
            error_found = True

    assert error_found, "Response does not contain 'Invalid credentials' error message"


test_post_api_v1_users_login_with_invalid_credentials()