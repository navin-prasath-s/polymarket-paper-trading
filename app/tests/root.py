import requests
import os
from dotenv import load_dotenv

load_dotenv()
URL =  os.getenv("API_BASE_URL")


def test_read_root():
    response = requests.get(f"{URL}/")
    assert response.json() == {"message": "Server is up and running"}