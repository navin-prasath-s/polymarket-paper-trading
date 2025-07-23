import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("INTERNAL_API_KEY")
URL =  os.getenv("API_BASE_URL")




def test_add_tradable_market_success():
    data = [
        {
            "condition_id": "test_market_123000",
            "market_slug": "market-123000"
        }
    ]
    headers = {"x-api-key": API_KEY}
    response = requests.post(f"{URL}/market", json=data, headers=headers)
    assert response.status_code == 201, response.text
    print("Success:", response.json())


def test_add_tradable_market_missing_api_key_return_422():
    data = [
        {
            "condition_id": "test_market_1230001",
            "market_slug": "market-1230001"
        }
    ]
    response = requests.post(f"{URL}/market", json=data)
    assert response.status_code == 422, response.text
    print("Missing key:", response.json())

def test_add_tradable_market_wrong_api_key_return_401():
    data = [
        {
            "condition_id": "test_market_1230002",
            "market_slug": "market-1230002"
        }
    ]
    headers = {"x-api-key": "wrongkey"}
    response = requests.post(f"{URL}/market", json=data, headers=headers)
    assert response.status_code == 401
    print("Wrong key:", response.json())

def test_add_tradable_market_empty_list_return_400():
    headers = {"x-api-key": API_KEY}
    response = requests.post(f"{URL}/market", json=[], headers=headers)
    assert response.status_code == 400
    print("Empty list:", response.json())


# TODO: Add tests for duplicate condition_id



def test_get_all_markets_success():
    response = requests.get(f"{URL}/market")
    assert response.status_code == 200
    print("Markets count:", len(response.json()))

def test_get_one_market_that_exists_success():
    id = "test_market_123000"
    response = requests.get(f"{URL}/market/{id}")
    assert response.status_code == 200
    print(response.json())

def test_get_one_market_that_does_not_exists_return_404():
    id = "doesntexists"
    response = requests.get(f"{URL}/market/{id}")
    assert response.status_code == 404
    print(response.json())



def test_patch_markets_untradable_success():
    data = [
        "test_market_123000"
    ]
    headers = {"x-api-key": API_KEY}
    response = requests.patch(f"{URL}/market/untradable/", json=data, headers=headers)
    assert response.status_code == 200, response.text
    print("Success:", response.json())

def test_patch_markets_untradable_wrong_api_key_return_401():
    data = [
        "test_market_123000"
    ]
    headers = {"x-api-key": "wrongkey"}
    response = requests.patch(f"{URL}/market/untradable/", json=data, headers=headers)
    assert response.status_code == 401, response.text
    print("Wrong API key:", response.json())

def test_patch_markets_untradable_empty_list_return_400():
    headers = {"x-api-key": API_KEY}
    response = requests.patch(f"{URL}/market/untradable/", json=[], headers=headers)
    assert response.status_code == 400, response.text
    print("Empty list:", response.json())



if __name__ == "__main__":
    test_add_tradable_market_success()
    test_add_tradable_market_missing_api_key_return_422()
    test_add_tradable_market_wrong_api_key_return_401()
    test_add_tradable_market_empty_list_return_400()
    test_get_all_markets_success()
    test_get_one_market_that_exists_success()
    test_get_one_market_that_does_not_exists_return_404()
    test_patch_markets_untradable_success()
    test_patch_markets_untradable_wrong_api_key_return_401()
    test_patch_markets_untradable_empty_list_return_400()

    # test_add_tradable_market_duplicate_condition_id_return_400()