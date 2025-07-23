import requests
import os
from dotenv import load_dotenv

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


def test_create_user_profile_success():
    payload = {
        "name": "User One",
        "user_name": "user_one"
    }
    token = get_token()
    response = requests.post(f"{URL}/user_profile",
                             json=payload,
                             cookies={'token': token})
    assert response.status_code == 201, response.text


def test_get_user_profile_success():
    token = get_token()
    response = requests.get(f"{URL}/user_profile",
                             cookies={'token': token})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "name" in data
    assert "user_name" in data
    assert "balance" in data
    assert data["balance"] == "1000.00"

if __name__ == "__main__":
    pass