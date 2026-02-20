import requests

BASE_URL = "http://localhost:8000//api/v1/"
LOGOUT_ENDPOINT = BASE_URL + "users/logout/"
TIMEOUT = 30

def test_post_api_v1_users_logout_without_authorization_header():
    try:
        response = requests.post(LOGOUT_ENDPOINT, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to logout endpoint failed: {e}"

    assert response.status_code == 401, f"Expected status code 401 but got {response.status_code}"
    try:
        json_response = response.json()
        expected_detail = "Authentication credentials were not provided."
        actual_detail = json_response.get("detail") if isinstance(json_response, dict) else None
        assert actual_detail == expected_detail, f"Expected detail message '{expected_detail}' but got '{actual_detail}'"
    except ValueError:
        assert False, "Response is not valid JSON"

test_post_api_v1_users_logout_without_authorization_header()
