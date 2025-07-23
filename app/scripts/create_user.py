import httpx

def create_user(payload: dict):
    response = httpx.post("http://127.0.0.1:8080/auth/register", json=payload)

    print(f"Status Code: {response.status_code}")
    try:
        print("JSON Response:")
        print(response.json())
    except Exception:
        print("Raw Response:")
        print(response.text)

if __name__ == "__main__":
    payload = {
        "email": "superuser@example.com",
        "password": "superuserpass"
    }

    # payload = {
    #     "email": "user1@example.com",
    #     "password": "user1pass"
    # }


    create_user(payload)