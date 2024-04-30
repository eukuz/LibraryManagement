def test_smoke(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_cookie(set_session_id, client):
    client.cookies = {'SESSION_ID': set_session_id}
    client.headers = {}
    resp = client.get('/')
    assert resp.status_code == 200


def test_unauthorized(client):
    client.cookies = {}
    client.headers = {}
    resp = client.get('/')
    assert resp.status_code == 401


def test_unauthorized_wrong_creds(set_session_id, client):
    client.cookies = {'SESSION_ID': set_session_id + "aboba"}
    client.headers = {}
    resp = client.get('/')
    assert resp.status_code == 401
