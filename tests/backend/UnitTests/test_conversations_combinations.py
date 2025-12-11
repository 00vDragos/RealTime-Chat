import itertools
import pytest


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_create_direct_conversations_for_pairs(client, ensure_test_users):
    tokens = {u["email"]: u["token"] for u in ensure_test_users}
    emails = ["ttt@test.com", "yyy@test.com", "uuu@test.com", "iii@test.com"]

    for a, b in itertools.combinations(emails, 2):
        # Create direct conversation with participants [a, b]
        # Backend expects participant_ids (UUIDs) excluding the creator
        # Fetch conversations to map emails->ids first if needed
        # Here we create a conversation by passing only the other participant's id
        # so we first create a lookup by calling /api/auth/me for each email
        user_ids = {}
        for e in emails:
            rme = await client.get("/api/auth/me", headers=_auth(tokens[e]))
            assert rme.status_code == 200
            user_ids[e] = rme.json()["id"]

        resp = await client.post(
            "/api/messages/new_conversation",
            headers=_auth(tokens[a]),
            json={"participant_ids": [user_ids[b]]},
        )
        assert resp.status_code in (200, 201, 409), resp.text

        # List conversations for both users
        for e in (a, b):
            rlist = await client.get(
                "/api/messages/conversations",
                headers=_auth(tokens[e]),
            )
            assert rlist.status_code == 200, rlist.text


@pytest.mark.anyio
async def test_create_group_conversations_for_triplets(client, ensure_test_users):
    tokens = {u["email"]: u["token"] for u in ensure_test_users}
    emails = ["ttt@test.com", "yyy@test.com", "uuu@test.com", "iii@test.com"]

    for group in itertools.combinations(emails, 3):
        creator = group[0]
        # Build participant_ids excluding creator
        user_ids = {}
        for e in group:
            rme = await client.get("/api/auth/me", headers=_auth(tokens[e]))
            assert rme.status_code == 200
            user_ids[e] = rme.json()["id"]
        participant_ids = [user_ids[e] for e in group if e != creator]

        resp = await client.post(
            "/api/messages/new_conversation",
            headers=_auth(tokens[creator]),
            json={"participant_ids": participant_ids, "group_name": "Test Group"},
        )
        assert resp.status_code in (200, 201, 409), resp.text

        # List for all group participants
        for e in group:
            rlist = await client.get(
                "/api/messages/conversations",
                headers=_auth(tokens[e]),
            )
            assert rlist.status_code == 200, rlist.text
