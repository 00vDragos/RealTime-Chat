import pytest


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_change_avatar_for_all_users(client, ensure_test_users):
    # Simple deterministic avatar URLs with cache busters
    base_urls = [
        "https://placekitten.com/200/200",
        "https://placedog.net/200/200",
        "https://picsum.photos/200",
        "https://placebear.com/200/200",
    ]

    # Change avatar for each user and verify via /api/auth/me
    for idx, u in enumerate(ensure_test_users):
        new_url = f"{base_urls[idx % len(base_urls)]}?t={idx}"
        resp = await client.patch(
            "/users/me/avatar",
            headers=_auth(u["token"]),
            json={"avatar_url": new_url},
        )
        assert resp.status_code == 200, resp.text
        updated = resp.json()
        assert updated.get("avatar_url") == new_url

        # Verify /api/auth/me reflects change
        me = await client.get("/auth/me", headers=_auth(u["token"]))
        assert me.status_code == 200, me.text
        assert me.json().get("avatar_url") == new_url
