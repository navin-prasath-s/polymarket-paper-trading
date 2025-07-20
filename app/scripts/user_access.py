import httpx

def get_user_by_id(token: str, user_id: int, label: str):
    print(f"\n--- {label} ---")
    response = httpx.get(
        f"http://127.0.0.1:8080/users/{user_id}",
        cookies={"token": token}
    )
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        print("JSON:", response.json())
    else:
        print("Response:", response.text)

if __name__ == "__main__":
    regular_user_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiYXVkIjpbImZhc3RhcGktdXNlcnM6YXV0aCJdLCJleHAiOjE3NTMwNTgzMDZ9.iNqgMIt7rIPP9I1q_bgaAHeeWe3Pc-jg8w4_TtMtt1I"
    superuser_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiYXVkIjpbImZhc3RhcGktdXNlcnM6YXV0aCJdLCJleHAiOjE3NTMwNTg0OTN9.pneLmLxUVf4cP3dfPrTyI-kYS6Ah3YwNo-OJWOTrw50"

    get_user_by_id(regular_user_token, user_id=3, label="Regular User (should fail)")
    get_user_by_id(superuser_token, user_id=3,label="Superuser (should succeed)")