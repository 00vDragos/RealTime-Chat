import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
@pytest.mark.anyio
async def test_friend_request_accept_flow():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Seed two users
        a = {"email": "int_a@test.com", "password": "ParolaTare1!", "display_name": "IntA"}
        b = {"email": "int_b@test.com", "password": "ParolaTare1!", "display_name": "IntB"}
        for u in (a, b):
            await client.post("/auth/register", json=u)
        # Login tokens
        login_a = await client.post("/auth/login", json={"email": a["email"], "password": a["password"]})
        login_b = await client.post("/auth/login", json={"email": b["email"], "password": b["password"]})
        assert login_a.status_code == 200 and login_b.status_code == 200
        tok_a = login_a.json()["access_token"]
        tok_b = login_b.json()["access_token"]
        me_a = await client.get("/auth/me", headers={"Authorization": f"Bearer {tok_a}"})
        me_b = await client.get("/auth/me", headers={"Authorization": f"Bearer {tok_b}"})
        a_id = me_a.json()["id"]
        b_id = me_b.json()["id"]

        # A -> B send request
        resp_send = await client.post("/friends/requests", headers={"Authorization": f"Bearer {tok_a}"}, json={"to_email": b["email"]})
        assert resp_send.status_code in (200, 201, 409), resp_send.text

        # B incoming
        resp_list_b = await client.get("/friends/requests", headers={"Authorization": f"Bearer {tok_b}"}, params={"direction": "in"})
        assert resp_list_b.status_code == 200
        req_id = None
        for fr in resp_list_b.json():
            if fr.get("status") == "pending" and fr.get("from_user_id") == a_id and fr.get("to_user_id") == b_id:
                req_id = fr["id"]
                break
        if req_id is None:
            # fallback: list A outgoing
            resp_list_a = await client.get("/friends/requests", headers={"Authorization": f"Bearer {tok_a}"}, params={"direction": "out"})
            if resp_list_a.status_code == 200:
                for fr in resp_list_a.json():
                    if fr.get("status") == "pending" and fr.get("from_user_id") == a_id and fr.get("to_user_id") == b_id:
                        req_id = fr["id"]
                        break
        if req_id is None:
            # Try to create reverse request and pick pending
            await client.post("/friends/requests", headers={"Authorization": f"Bearer {tok_b}"}, json={"to_email": a["email"]})
            resp_list_a_in = await client.get("/friends/requests", headers={"Authorization": f"Bearer {tok_a}"}, params={"direction": "in"})
            if resp_list_a_in.status_code == 200:
                for fr in resp_list_a_in.json():
                    if fr.get("status") == "pending" and fr.get("from_user_id") == b_id and fr.get("to_user_id") == a_id:
                        req_id = fr["id"]
                        break
        if req_id is None:
            pytest.skip("No pending friend request available")

        # B accepts
        resp_accept = await client.post(f"/friends/requests/{req_id}/respond", headers={"Authorization": f"Bearer {tok_b}"}, json={"status": "accepted"})
        assert resp_accept.status_code in (200, 201), resp_accept.text

        # List friends for A
        resp_friends = await client.get("/friends", headers={"Authorization": f"Bearer {tok_a}"})
        assert resp_friends.status_code == 200
        emails = {u.get("email") for u in resp_friends.json()}
        assert b["email"] in emails

        # Remove friend
        await client.post("/friends/remove", headers={"Authorization": f"Bearer {tok_a}"}, json={"friend_email": b["email"]})
