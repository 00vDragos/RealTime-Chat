import pytest


@pytest.mark.anyio
async def test_list_conversations_ok(client, ensure_test_users):
    token = ensure_test_users[0]["token"]
    resp = await client.get("/messages/conversations", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    # Each item should have basic keys
    if data:
        item = data[0]
        assert "id" in item
        assert "friendName" in item or "participantNames" in item
