import pytest


@pytest.mark.anyio
async def test_login_all_users(client, test_users):
    for user in test_users:
        resp = await client.post("/api/auth/login", json={
            "email": user["email"],
            "password": user["password"],
        })
        assert resp.status_code == 200, f"Login failed for {user['email']}: {resp.text}"
        data = resp.json()
        assert "access_token" in data and data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_auth_me_all_users(client, ensure_test_users):
    emails = {"ttt@test.com", "yyy@test.com", "uuu@test.com", "iii@test.com"}
    for u in ensure_test_users:
        token = u["token"]
        resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200, f"/me failed for {u['email']}: {resp.text}"
        me = resp.json()
        assert me["email"] in emails
        assert me.get("id")
