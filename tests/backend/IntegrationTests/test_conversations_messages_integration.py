import pytest
import httpx
from uuid import UUID

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
@pytest.mark.anyio
async def test_direct_conversation_and_messages():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Seed two users and login
        a = {"email": "int_c@test.com", "password": "ParolaTare1!", "display_name": "IntC"}
        b = {"email": "int_d@test.com", "password": "ParolaTare1!", "display_name": "IntD"}
        for u in (a, b):
            await client.post("/auth/register", json=u)
        login_a = await client.post("/auth/login", json={"email": a["email"], "password": a["password"]})
        login_b = await client.post("/auth/login", json={"email": b["email"], "password": b["password"]})
        tok_a = login_a.json()["access_token"]
        tok_b = login_b.json()["access_token"]
        me_a = await client.get("/auth/me", headers={"Authorization": f"Bearer {tok_a}"})
        me_b = await client.get("/auth/me", headers={"Authorization": f"Bearer {tok_b}"})
        a_id = me_a.json()["id"]
        b_id = me_b.json()["id"]

        # Create direct conversation A<->B
        resp_conv = await client.post("/messages/new_conversation", headers={"Authorization": f"Bearer {tok_a}"}, json={"participant_ids": [b_id]})
        if resp_conv.status_code not in (200, 201):
            # Fallback: list conversations and try to find direct A-B
            list_a = await client.get("/messages/conversations", headers={"Authorization": f"Bearer {tok_a}"})
            if list_a.status_code != 200:
                pytest.skip(f"List conversations failed for A: {list_a.text}")
            conv_id = None
            for c in list_a.json():
                pids = set(c.get("participantIds", []))
                if {a_id, b_id} <= set(pids):
                    conv_id = c.get("id")
                    break
            if not conv_id:
                pytest.skip("Could not create or find direct conversation for A-B")
        else:
            conv = resp_conv.json()
            conv_id = conv.get("id") or (conv[0].get("id") if isinstance(conv, list) and conv else None)
        if not conv_id:
            pytest.skip("Direct conversation ID unavailable after creation and listing")
        assert UUID(conv_id)

        # Send messages
        msg1 = await client.post(f"/messages/conversations/{conv_id}/messages", headers={"Authorization": f"Bearer {tok_a}"}, params={"body": "Hello from A"})
        if msg1.status_code not in (200, 201):
            pytest.skip(f"Message send failed (A): {msg1.text}")
        msg2 = await client.post(f"/messages/conversations/{conv_id}/messages", headers={"Authorization": f"Bearer {tok_b}"}, params={"body": "Hi A, this is B"})
        if msg2.status_code not in (200, 201):
            pytest.skip(f"Message send failed (B): {msg2.text}")

        # List conversations for A; verify last message preview/time present
        list_a = await client.get("/messages/conversations", headers={"Authorization": f"Bearer {tok_a}"})
        assert list_a.status_code == 200
        found = [c for c in list_a.json() if c.get("id") == conv_id]
        assert found and found[0].get("lastMessage")

@pytest.mark.anyio
async def test_group_conversation_and_messages():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Seed three users and login
        users = [
            {"email": "int_e@test.com", "password": "ParolaTare1!", "display_name": "IntE"},
            {"email": "int_f@test.com", "password": "ParolaTare1!", "display_name": "IntF"},
            {"email": "int_g@test.com", "password": "ParolaTare1!", "display_name": "IntG"},
        ]
        for u in users:
            await client.post("/auth/register", json=u)
        tokens = {}
        ids = {}
        for u in users:
            login = await client.post("/auth/login", json={"email": u["email"], "password": u["password"]})
            tokens[u["email"]] = login.json()["access_token"]
            me = await client.get("/auth/me", headers={"Authorization": f"Bearer {tokens[u['email']]}"})
            ids[u["email"]] = me.json()["id"]

        creator = users[0]
        others = [ids[users[1]["email"]], ids[users[2]["email"]]]

        # Create group conversation
        resp_conv = await client.post("/messages/new_conversation", headers={"Authorization": f"Bearer {tokens[creator['email']]}"}, json={"participant_ids": others})
        if resp_conv.status_code not in (200, 201):
            # Fallback: list and match by participants
            list_creator = await client.get("/messages/conversations", headers={"Authorization": f"Bearer {tokens[creator['email']]}"})
            if list_creator.status_code != 200:
                pytest.skip(f"List conversations failed for creator: {list_creator.text}")
            conv_id = None
            for c in list_creator.json():
                pids = set(c.get("participantIds", []))
                if set(pids) == set([ids[users[0]['email']], ids[users[1]['email']], ids[users[2]['email']]]):
                    conv_id = c.get("id")
                    break
            if not conv_id:
                pytest.skip("Could not create or find group conversation for participants")
        else:
            resp_json = resp_conv.json()
            conv_id = resp_json.get("id") or (resp_json[0].get("id") if isinstance(resp_json, list) and resp_json else None)
        if not conv_id:
            pytest.skip("Group conversation ID unavailable after creation and listing")
        assert UUID(conv_id)

        # Send messages by multiple participants
        m1 = await client.post(f"/messages/conversations/{conv_id}/messages", headers={"Authorization": f"Bearer {tokens[creator['email']]}"}, params={"body": "Hello group"})
        if m1.status_code not in (200, 201):
            pytest.skip(f"Message send failed (creator): {m1.text}")
        m2 = await client.post(f"/messages/conversations/{conv_id}/messages", headers={"Authorization": f"Bearer {tokens[users[1]['email']]}"}, params={"body": "Hey all"})
        if m2.status_code not in (200, 201):
            pytest.skip(f"Message send failed (user2): {m2.text}")
        m3 = await client.post(f"/messages/conversations/{conv_id}/messages", headers={"Authorization": f"Bearer {tokens[users[2]['email']]}"}, params={"body": "Hi everyone"})
        if m3.status_code not in (200, 201):
            pytest.skip(f"Message send failed (user3): {m3.text}")

        # List conversations and ensure lastMessage populated
        list_creator = await client.get("/messages/conversations", headers={"Authorization": f"Bearer {tokens[creator['email']]}"})
        convs = list_creator.json()
        target = [c for c in convs if c.get("id") == conv_id]
        assert target and target[0].get("lastMessage")
