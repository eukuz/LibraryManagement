from unittest import mock

from api import di


def test_empty_redirect(client):
    resp = client.get("/api/yndx-oauth/redirect")
    assert resp.status_code == 500


def test_error(client):
    resp = client.get("/api/yndx-oauth/redirect", params={'error': 'aboba'})
    assert resp.status_code == 500

    resp = client.get("/api/yndx-oauth/redirect", params={'code': 1, 'error': 'aboba'})
    assert resp.status_code == 500


def test_happypath(app, client):
    mock_http_client = mock.AsyncMock()
    app.dependency_overrides[di.http_client] = lambda: mock_http_client
    resp = client.get("/api/yndx-oauth/redirect", params={'code': 1})
    assert resp.status_code == 200, resp.content
    assert mock_http_client.assert_called()
