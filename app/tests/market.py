import requests
import os
from dotenv import load_dotenv

load_dotenv()
URL =  os.getenv("API_BASE_URL")

def test_get_all_markets():
    response = requests.get(f"{URL}market/")
    assert response.status_code == 200
    print(response.json())
