import uuid

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def _register_and_token() -> str:
    email = f"jobs-{uuid.uuid4().hex[:8]}@example.com"
    password = "JobsTest123!"
    r = client.post(
        "/users/register",
        json={"email": email, "password": password, "full_name": "Jobs Tester"},
    )
    assert r.status_code == 201
    login = client.post("/users/login", json={"email": email, "password": password})
    assert login.status_code == 200
    return login.json()["access_token"]


def test_integrations_status_requires_auth() -> None:
    res = client.get("/integrations/status")
    assert res.status_code == 401


def test_integrations_status_authenticated() -> None:
    token = _register_and_token()
    res = client.get(
        "/integrations/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    names = {item["provider"] for item in body}
    assert "linkedin" in names
    assert "glassdoor" in names
    assert "rss_feed" in names
    assert len(names) >= 10


def test_jobs_discover_fake_and_matches() -> None:
    token = _register_and_token()
    headers = {"Authorization": f"Bearer {token}"}

    disc = client.post("/jobs/discover/fake", headers=headers)
    assert disc.status_code == 200
    data = disc.json()
    assert "created_jobs" in data
    assert data["total_fake_jobs"] == 2

    matches = client.get("/jobs/matches", headers=headers)
    assert matches.status_code == 200
    rows = matches.json()
    assert len(rows) >= 2
    titles = {r["title"] for r in rows}
    assert "Backend Engineer" in titles

    apps = client.get("/jobs/applications", headers=headers)
    assert apps.status_code == 200
    assert len(apps.json()) >= 2
    for row in apps.json():
        assert "job_title" in row
        assert "status_detail" in row


def test_discover_providers_and_auto_apply_manual_fallback() -> None:
    token = _register_and_token()
    headers = {"Authorization": f"Bearer {token}"}

    disc = client.post("/jobs/discover/providers", headers=headers)
    assert disc.status_code == 200
    assert disc.json()["providers_touched"] >= 8

    auto = client.post("/jobs/applications/auto-apply/run", headers=headers)
    assert auto.status_code == 200
    data = auto.json()
    assert data.get("manual_required", 0) >= 1

    apps = client.get("/jobs/applications", headers=headers)
    rows = apps.json()
    manual = [r for r in rows if r["status"] == "manual_required"]
    assert len(manual) >= 1

    app_id = manual[0]["id"]
    done = client.post(f"/jobs/applications/{app_id}/manual-complete", headers=headers)
    assert done.status_code == 200
    assert done.json()["status"] == "manual_completed"
