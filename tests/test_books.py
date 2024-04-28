

import pytest


def test_no_book(client):
    resp = client.get("/api/books/-1")
    assert resp.status_code == 404


def test_existent_book(client):
    resp = client.get("/api/books/1")
    assert resp.status_code == 200


def test_appears_in_collection_unexistent_book(client):
    resp = client.post("/api/books/-1/collection?add=true")
    assert resp.status_code == 404

    resp = client.post("/api/books/-1/collection?add=false")
    assert resp.status_code == 404


def test_appears_in_collection(client):
    resp = client.get("/api/books/1")
    assert resp.status_code == 200
    resp = resp.json()
    assert resp["in_collection"] is False, resp

    resp = client.post("/api/books/1/collection?add=true")
    assert resp.status_code == 200

    resp = client.get("/api/books/1")
    assert resp.status_code == 200
    resp = resp.json()
    assert resp["in_collection"] is True, resp

    resp = client.post("/api/books/1/collection?add=false")
    assert resp.status_code == 200

    resp = client.get("/api/books/1")
    assert resp.status_code == 200
    resp = resp.json()
    assert resp["in_collection"] is False, resp


def test_set_progress_unexistent_book(client):
    resp = client.post("/api/books/-1/progress", json={'pages_read': 10})
    assert resp.status_code == 404


def test_set_progress(client):
    resp = client.get("/api/books/1")
    assert resp.status_code == 200
    assert resp.json()["read_pages"] == 0

    resp = client.post("/api/books/1/progress", json={'pages_read': 10})
    assert resp.status_code == 200

    resp = client.get("/api/books/1")
    assert resp.status_code == 200
    assert resp.json()["read_pages"] == 10

    resp = client.post("/api/books/1/progress", json={'pages_read': 20})
    assert resp.status_code == 200

    resp = client.get("/api/books/1")
    assert resp.status_code == 200
    assert resp.json()["read_pages"] == 20


@pytest.mark.parametrize(
    ('params', 'expected_ids'),
    (
        ({}, (1, 2)),
        ({'title_like': '1'}, (1,)),
        ({'title_like': '2'}, (2,)),
        ({'author_like': '1'}, (1,)),
        ({'author_like': '2'}, (2,)),
        ({'title_like': '1', 'author_like': '1'}, (1,)),
        ({'title_like': '1', 'author_like': '2'}, ()),
    )
)
def test_search_books(client, params, expected_ids):
    resp = client.get("/api/books", params=params)
    assert resp.status_code == 200

    books = resp.json()['books']
    expected_ids = set(expected_ids)
    ids = set([book['id'] for book in books])

    assert ids == expected_ids


def test_suggest_books(client):
    resp = client.get("/api/books/suggest")
    assert resp.status_code == 200

    books = resp.json()['books']
    expected_ids = set([1, 2])
    ids = set([book['id'] for book in books])

    assert ids == expected_ids
