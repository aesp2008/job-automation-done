import uuid

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def _register_and_token() -> str:
    email = f"rss-{uuid.uuid4().hex[:8]}@example.com"
    password = "RssTest123!"
    r = client.post(
        "/users/register",
        json={"email": email, "password": password, "full_name": "RSS Tester"},
    )
    assert r.status_code == 201
    login = client.post("/users/login", json={"email": email, "password": password})
    assert login.status_code == 200
    return login.json()["access_token"]


def test_reject_localhost_rss_url() -> None:
    token = _register_and_token()
    res = client.put(
        "/integrations/connections/rss_feed",
        headers={"Authorization": f"Bearer {token}"},
        json={"rss_url": "http://127.0.0.1/feed.xml"},
    )
    assert res.status_code == 400


def test_upsert_and_list_rss_connection() -> None:
    token = _register_and_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://www.reddit.com/r/forhire/.rss"
    res = client.put("/integrations/connections/rss_feed", headers=headers, json={"rss_url": url})
    assert res.status_code == 200
    assert res.json()["rss_url"] == url

    lst = client.get("/integrations/connections", headers=headers)
    assert lst.status_code == 200
    rows = lst.json()
    assert any(r["provider"] == "rss_feed" for r in rows)

    status = client.get("/integrations/status", headers=headers)
    rss = next(s for s in status.json() if s["provider"] == "rss_feed")
    assert rss["connected"] is True

    rm = client.delete("/integrations/connections/rss_feed", headers=headers)
    assert rm.status_code == 200
    lst2 = client.get("/integrations/connections", headers=headers)
    assert not any(r["provider"] == "rss_feed" for r in lst2.json())
