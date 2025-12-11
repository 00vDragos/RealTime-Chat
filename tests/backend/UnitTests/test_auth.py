import pytest


@pytest.mark.anyio
async def test_login_success(client, ensure_test_users):
    # Use one of the seeded users
    payload = {"email": "ttt@test.com", "password": "parolatare1!"}
    resp = await client.post("/api/auth/login", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_auth_me_returns_user(client, ensure_test_users):
    # Pick the first user's token
    token = ensure_test_users[0]["token"]
    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    user = resp.json()
    assert user["email"] in {"ttt@test.com", "yyy@test.com", "uuu@test.com", "iii@test.com"}
    assert "id" in user
