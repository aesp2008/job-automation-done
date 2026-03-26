import uuid

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_register_login_me_flow() -> None:
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123!"

    register_res = client.post(
        "/users/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert register_res.status_code == 201
    assert register_res.json()["email"] == email

    login_res = client.post("/users/login", json={"email": email, "password": password})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token

    me_res = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

