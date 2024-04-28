from unittest import mock

from api import di
from api.routers import yndx_oauth


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

    access_token_mock = mock.MagicMock()
    access_token_mock.json = mock.MagicMock()
    access_token_mock.json.return_value = {'access_token': '1'}

    user_mock = mock.MagicMock()
    user_mock.json = mock.MagicMock()
    user_mock.json.return_value = yndx_oauth._UserData(display_name='a', id='123').model_dump()

    def side_effect(*args, **kwargs):
        if 'token' in args[0]:
            return access_token_mock
        if 'info' in args[0]:
            return user_mock
        raise Exception(*args, **kwargs)
    mock_http_client.post = mock.AsyncMock()
    mock_http_client.post.side_effect = side_effect
    mock_http_client.get.side_effect = side_effect

    app.dependency_overrides[di.http_client] = lambda: mock_http_client
    resp = client.get("/api/yndx-oauth/redirect", params={'code': 1}, follow_redirects=False)
    assert resp.status_code == 307, resp.content
