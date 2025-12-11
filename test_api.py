import requests
import json

BASE_URL = "http://localhost:5000"


def pretty(response):
    """Utility to print formatted output."""
    print(f"Status: {response.status_code}")
    try:
        print("Response:", json.dumps(response.json(), indent=2))
    except Exception:
        print("Response (raw):", response.text)
    print("\n")


def test_get_books():
    response = requests.get(f"{BASE_URL}/books")
    pretty(response)


def test_add_book():
    payload = {
        "title": "Python Guide",
        "author": "Guido van Rossum"
    }

    response = requests.post(
        f"{BASE_URL}/books",
        json=payload
    )
    pretty(response)


def test_delete_book(book_id):
    response = requests.delete(f"{BASE_URL}/books/{book_id}")
    pretty(response)


if __name__ == "__main__":
    print("➡️ Testing GET books")
    test_get_books()

    print("➡️ Testing ADD book")
    test_add_book()

    print("➡️ Testing GET books again")
    test_get_books()

    print("➡️ Testing DELETE book id=1")
    test_delete_book(1)

    print("➡️ Testing GET books again")
    test_get_books()
