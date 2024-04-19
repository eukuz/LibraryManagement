from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
import pytest_asyncio

from api.services import books


@pytest_asyncio.fixture
async def data_filler(sessionmaker: async_sessionmaker[AsyncSession]):
    id_ = await books.add_book("1", "author1", "genre1", 100, sessionmaker)

    yield id_


def test_no_book(client):
    resp = client.get("/api/books/-1")
    assert resp.status_code == 404


def test_existent_book(client, data_filler):
    resp = client.get(f"/api/books/{data_filler}")
    assert resp.status_code == 200


def test_appears_in_collection_unexistent_book(client):
    resp = client.post("/api/books/-1/collection?add=true")
    assert resp.status_code == 404

    resp = client.post("/api/books/-1/collection?add=false")
    assert resp.status_code == 404


def test_appears_in_collection(client, data_filler):
    resp = client.get(f"/api/books/{data_filler}")
    assert resp.status_code == 200
    resp = resp.json()
    assert resp["in_collection"] is False, resp

    resp = client.post(f"/api/books/{data_filler}/collection?add=true")
    assert resp.status_code == 200

    resp = client.get(f"/api/books/{data_filler}")
    assert resp.status_code == 200
    resp = resp.json()
    assert resp["in_collection"] is True, resp

    resp = client.post(f"/api/books/{data_filler}/collection?add=false")
    assert resp.status_code == 200

    resp = client.get(f"/api/books/{data_filler}")
    assert resp.status_code == 200
    resp = resp.json()
    assert resp["in_collection"] is False, resp


def test_set_progress_unexistent_book(client):
    resp = client.post("/api/books/-1/progress", json={'pages_read': 10})
    assert resp.status_code == 404


def test_set_progress(client, data_filler):
    resp = client.get(f"/api/books/{data_filler}")
    assert resp.status_code == 200
    assert resp.json()["read_pages"] == 0

    resp = client.post(f"/api/books/{data_filler}/progress", json={'pages_read': 10})
    assert resp.status_code == 200

    resp = client.get(f"/api/books/{data_filler}")
    assert resp.status_code == 200
    assert resp.json()["read_pages"] == 10
