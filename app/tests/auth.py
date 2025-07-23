import requests
import os
from dotenv import load_dotenv
from requests import Response

load_dotenv()
URL = os.getenv("API_BASE_URL")


def get_token():
    payload = {
        "username": "user1@example.com",
        "password": "user1pass"
    }
    response = requests.post(
        f"{URL}/auth/jwt/login",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 204, response.text

    jwt_token = response.cookies.get("token")
    assert jwt_token, "JWT cookie not found in response"
    return jwt_token



def test_login_user_success():
    payload = {
        "username": "user1@example.com",
        "password": "user1pass"
    }
    response = requests.post(f"{URL}/auth/jwt/login",
                             data=payload,
                             headers={"Content-Type": "application/x-www-form-urlencoded"})

    print("Headers:", response.headers)
    assert response.status_code == 204, response.text


def login_user_wrong_password_return_400():
    payload = {
        "username": "user1@example.com",
        "password": "user1pass11"
    }
    response: Response = requests.post(f"{URL}/auth/jwt/login",
                             data=payload,
                             headers={"Content-Type": "application/x-www-form-urlencoded"})

    assert response.status_code == 400
    assert response.json() == {"detail":"LOGIN_BAD_CREDENTIALS"}



def test_get_current_user_success():
    token = get_token()
    response = requests.get(
        f"{URL}/users/me",
        cookies={"token": token}
    )
    assert response.status_code == 200, response.text


def test_get_current_user_wrong_token_return_401():
    token = "wrongtoken"
    response = requests.get(
        f"{URL}/users/me",
        cookies={"token": token}
    )
    assert response.status_code == 401, response.text

def test_get_current_user_missing_token_401():
    response = requests.get(
        f"{URL}/users/me",
    )
    assert response.status_code == 401, response.text



if __name__ == "__main__":
    test_login_user_success()
    login_user_wrong_password_return_400()
    test_get_current_user_success()
    test_get_current_user_wrong_token_return_401()
    test_get_current_user_missing_token_401()