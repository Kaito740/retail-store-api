import requests

BASE_URL = "http://localhost:8000/api/v1/"
LOGIN_URL = BASE_URL + "users/login/"
LOGOUT_URL = BASE_URL + "users/logout/"
TIMEOUT = 30

USERNAME = "testing"
PASSWORD = "testing123"


def test_post_api_v1_users_logout_with_valid_token():
    try:
        # Step 1: Login to obtain a valid token
        login_response = requests.post(
            LOGIN_URL,
            json={"username": USERNAME, "password": PASSWORD},
            timeout=TIMEOUT,
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        login_data = login_response.json()
        token = login_data.get("token")
        assert token and isinstance(token, str), "Token not found in login response"

        headers = {"Authorization": f"Token {token}"}

        # Step 2: Call logout endpoint with valid token
        logout_response = requests.post(
            LOGOUT_URL,
            headers=headers,
            timeout=TIMEOUT,
        )
        assert logout_response.status_code == 200, f"Logout failed: {logout_response.text}"

        # Check if response is JSON string or plain text
        try:
            logout_msg = logout_response.json()  # may raise if not JSON
        except ValueError:
            logout_msg = logout_response.text.strip()

        if isinstance(logout_msg, str):
            assert logout_msg == "Successfully logged out", \
                "Logout success message not found or incorrect in response"
        else:
            # If JSON is something else, fail
            assert False, "Logout response is not a string message"

        # Step 3: Confirm token is invalidated by attempting a call with the same token
        check_response = requests.get(
            BASE_URL + "users/",
            headers=headers,
            timeout=TIMEOUT,
        )
        # After logout, token should be invalid, so expect 401 Unauthorized
        assert check_response.status_code == 401, \
            "Token was not invalidated after logout"

    except requests.RequestException as e:
        raise AssertionError(f"Request failed: {e}")


test_post_api_v1_users_logout_with_valid_token()
