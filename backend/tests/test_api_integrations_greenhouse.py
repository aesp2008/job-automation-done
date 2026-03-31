import uuid

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def _register_and_token() -> str:
    email = f"gh-{uuid.uuid4().hex[:8]}@example.com"
    password = "GhTest123!"
    r = client.post(
        "/users/register",
        json={"email": email, "password": password, "full_name": "GH Tester"},
    )
    assert r.status_code == 201
    login = client.post("/users/login", json={"email": email, "password": password})
    assert login.status_code == 200
    return login.json()["access_token"]


def test_greenhouse_connection_crud() -> None:
    token = _register_and_token()
    headers = {"Authorization": f"Bearer {token}"}

    bad = client.put(
        "/integrations/connections/greenhouse",
        headers=headers,
        json={"board_tokens": ["Invalid_Slug!"]},
    )
    assert bad.status_code == 422

    ok = client.put(
        "/integrations/connections/greenhouse",
        headers=headers,
        json={"board_tokens": ["stripe", "figma"]},
    )
    assert ok.status_code == 200

    st = client.get("/integrations/status", headers=headers)
    gh = next(s for s in st.json() if s["provider"] == "greenhouse_api")
    assert gh["connected"] is True

    rm = client.delete("/integrations/connections/greenhouse", headers=headers)
    assert rm.status_code == 200
