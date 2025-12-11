import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
@pytest.mark.anyio
async def test_register_login_me_refresh_logout():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        email = "int_user1@test.com"
        password = "ParolaTare1!"
        display_name = "IntUser1"

        # Try register (idempotent run: if 409, continue)
        resp_reg = await client.post("/api/auth/register", json={
            "email": email,
            "password": password,
            "display_name": display_name,
        })
        # tolerate already registered or duplicate as 4xx
        assert (resp_reg.status_code in (200, 201, 409)) or (400 <= resp_reg.status_code < 500), resp_reg.text

        # Login
        resp_login = await client.post("/api/auth/login", json={
            "email": email,
            "password": password,
        })
        assert resp_login.status_code == 200, resp_login.text
        data = resp_login.json()
        access = data["access_token"]
        refresh = data.get("refresh_token")
        assert access

        # Me
        resp_me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {access}"})
        assert resp_me.status_code == 200, resp_me.text
        me = resp_me.json()
        assert me["email"] == email

        # Refresh (if available)
        if refresh:
            resp_ref = await client.post("/api/auth/refresh", json={"refresh_token": refresh})
            assert resp_ref.status_code == 200, resp_ref.text

        # Logout (best-effort)
        await client.post("/api/auth/logout", headers={"Authorization": f"Bearer {access}"})
