import requests
import time
import json

BASE_URL = "http://localhost:5000"


def pretty(resp):
    print(f"Status: {resp.status_code}")
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text)
    print()


def add_book(title, author, year=2025):
    payload = {"title": title, "author": author, "year": year}
    r = requests.post(f"{BASE_URL}/books", json=payload)
    pretty(r)
    return r


def find_book_by_title(title):
    r = requests.get(f"{BASE_URL}/books")
    pretty(r)
    if r.status_code != 200:
        return None
    books = r.json().get('books', [])
    for b in books:
        if b.get('title') == title:
            return b
    return None


def delete_book(book_id):
    r = requests.delete(f"{BASE_URL}/books/{book_id}")
    pretty(r)
    return r


if __name__ == '__main__':
    unique_title = f"DB Test {int(time.time())}"
    print("Adding book:")
    add_resp = add_book(unique_title, "db-tester", 2025)
    if add_resp.status_code != 201:
        print("Failed to add book; aborting")
        exit(1)

    print("Verifying persistence:")
    found = find_book_by_title(unique_title)
    if not found:
        print("Book not found in GET /books — persistence failed")
        exit(2)

    print(f"Found book id={found['id']}; deleting it:")
    delete_book(found['id'])
    print("Done")
