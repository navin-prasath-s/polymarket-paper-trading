import httpx

def logout_user(token: str):
    response = httpx.post(
        "http://127.0.0.1:8080/auth/jwt/logout",
        cookies={"token": token}
    )
    print(f"Status Code: {response.status_code}")
    print("Response Headers:", response.headers)
    try:
        print("JSON Response:", response.json())
    except Exception:
        print("No JSON response; likely 204 No Content")

if __name__ == "__main__":
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiYXVkIjpbImZhc3RhcGktdXNlcnM6YXV0aCJdLCJleHAiOjE3NTMwNTgzMDZ9.iNqgMIt7rIPP9I1q_bgaAHeeWe3Pc-jg8w4_TtMtt1I"
    logout_user(token)