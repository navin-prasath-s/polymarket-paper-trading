import httpx

def get_current_user(token_cookie: str):
    response = httpx.get(
        "http://127.0.0.1:8080/users/me",
        cookies={"token": token_cookie}
    )
    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiYXVkIjpbImZhc3RhcGktdXNlcnM6YXV0aCJdLCJleHAiOjE3NTMwNDgyMTF9.AzTgdgSOSuyIPfqeoWFWEL3YE6sl9qNjPmrB8nQydSE"

    get_current_user(token)

