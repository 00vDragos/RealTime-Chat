import itertools
import pytest


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_send_and_list_messages_direct(client, ensure_test_users):
    tokens = {u["email"]: u["token"] for u in ensure_test_users}
    emails = ["ttt@test.com", "yyy@test.com", "uuu@test.com", "iii@test.com"]

    # Build direct conversations for each pair
    for a, b in itertools.combinations(emails, 2):
        # Create direct conversation via participant_ids from /api/messages/new_conversation requires UUIDs.
        # If API expects IDs, we first list conversations and pick/create one.
        # Here we list conversations to find or create using new_conversation by emails is not supported.
        # Fallback: creator lists conversations and picks existing after a message is sent.

        # Send a message to a conversation must have conversation_id; we first create a conversation via the API with IDs.
        # To get IDs, call /api/auth/me for both users is not strictly needed if conversation exists.
        # Instead, let a create conversation with participants via listing current conversations and ensuring one exists.

        # Create conversation via /api/messages/new_conversation is available but expects participant_ids.
        # We skip pre-creation and rely on sending requiring an existing conversation.
        # So we first create a conversation properly:
        # Step 1: Get user IDs via /api/auth/me
        ra = await client.get("/auth/me", headers=_auth(tokens[a]))
        rb = await client.get("/auth/me", headers=_auth(tokens[b]))
        ida = ra.json()["id"]
        idb = rb.json()["id"]

        # Backend expects participant_ids excluding creator. Pass only the other participant.
        rc = await client.post(
            "/messages/new_conversation",
            headers=_auth(tokens[a]),
            json={"participant_ids": [idb]},
        )
        assert rc.status_code in (200, 201, 409), rc.text
        conv = rc.json()
        conv_id = conv["id"] if isinstance(conv, dict) and "id" in conv else conv.get("conversationId", None)
        # If summary format differs, list conversations and pick one involving both users
        if not conv_id:
            rlist = await client.get("/messages/conversations", headers=_auth(tokens[a]))
            assert rlist.status_code == 200, rlist.text
            found = None
            for c in rlist.json():
                pids = set(c.get("participantIds", []))
                if ida in pids and idb in pids:
                    found = c
                    break
            assert found, "Conversation not found after creation"
            conv_id = found["id"] if "id" in found else found.get("conversationId")
        assert conv_id, "Conversation id missing"

        # Send message from A
        rm = await client.post(
            f"/conversations/{conv_id}/messages",
            headers=_auth(tokens[a]),
            params={"body": f"Hello from {a} to {b}"},
        )
        assert rm.status_code == 200, rm.text
        msg = rm.json()
        assert msg["body"].startswith("Hello from")

        # List messages for both
        for e in (a, b):
            rmsgs = await client.get(f"/conversations/{conv_id}/messages", headers=_auth(tokens[e]))
            assert rmsgs.status_code == 200, rmsgs.text
            assert isinstance(rmsgs.json(), list)


@pytest.mark.anyio
async def test_send_messages_group(client, ensure_test_users):
    tokens = {u["email"]: u["token"] for u in ensure_test_users}
    emails = ["ttt@test.com", "yyy@test.com", "uuu@test.com"]

    # Get IDs
    ids = []
    for e in emails:
        r = await client.get("/auth/me", headers=_auth(tokens[e]))
        ids.append(r.json()["id"])

    # Exclude creator from participant_ids
    rc = await client.post(
        "/messages/new_conversation",
        headers=_auth(tokens[emails[0]]),
        json={"participant_ids": ids[1:]},
    )
    assert rc.status_code in (200, 201, 409), rc.text
    conv = rc.json()
    conv_id = conv.get("id") or conv.get("conversationId")
    # Ensure conv_id is a string UUID; if missing, list and find by participants
    if isinstance(conv_id, dict):
        conv_id = conv_id.get("id")
    if not conv_id:
        rlist = await client.get("/messages/conversations", headers=_auth(tokens[emails[0]]))
        assert rlist.status_code == 200, rlist.text
        # Build expected participant set (creator + others)
        ids_full = []
        for e in emails:
            rme = await client.get("/auth/me", headers=_auth(tokens[e]))
            ids_full.append(rme.json()["id"])
        expected = set(ids_full)
        for c in rlist.json():
            pids = set(c.get("participantIds", []))
            if pids == expected:
                conv_id = c.get("id") or c.get("conversationId")
                break
    assert isinstance(conv_id, str) and len(conv_id) > 0

    # Send from all
    for e in emails:
        rm = await client.post(
            f"/conversations/{conv_id}/messages",
            headers=_auth(tokens[e]),
            params={"body": f"Message from {e}"},
        )
        assert rm.status_code == 200, rm.text

    # List
    for e in emails:
        rmsgs = await client.get(f"/conversations/{conv_id}/messages", headers=_auth(tokens[e]))
        assert rmsgs.status_code == 200, rmsgs.text
        assert len(rmsgs.json()) >= 3
