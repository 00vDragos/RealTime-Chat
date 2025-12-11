import pytest


@pytest.mark.anyio
async def test_update_avatar_requires_token(client):
    resp = await client.patch("/api/users/me/avatar", json={"avatar_url": "https://placedog.net/256/256"})
    assert resp.status_code in (401, 403)


@pytest.mark.anyio
async def test_update_avatar_success(client, ensure_test_users):
    # Use first seeded user token
    token = ensure_test_users[0]["token"]
    resp = await client.patch(
        "/api/users/me/avatar",
        headers={"Authorization": f"Bearer {token}"},
        json={"avatar_url": "https://placedog.net/256/256"},
    )
    assert resp.status_code == 200, resp.text
    user = resp.json()
    assert user.get("avatar_url") is not None
