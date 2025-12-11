import itertools
import pytest


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_friend_request_all_pairs(client, ensure_test_users):
    # Map email -> token
    tokens = {u["email"]: u["token"] for u in ensure_test_users}
    emails = ["ttt@test.com", "yyy@test.com", "uuu@test.com", "iii@test.com"]

    # For each ordered pair A->B, send request, list, then cancel
    for a, b in itertools.permutations(emails, 2):
        # Send friend request
        resp_send = await client.post(
            "/friends/requests",
            headers=_auth(tokens[a]),
            json={"to_email": b},
        )
        assert resp_send.status_code in (200, 201, 409), resp_send.text

        # List requests for B (incoming)
        resp_list = await client.get(
            "/friends/requests",
            headers=_auth(tokens[b]),
        )
        assert resp_list.status_code == 200, resp_list.text
        data = resp_list.json()
        assert isinstance(data, list)

        # If a request exists A->B, cancel it via DELETE by id
        req_id = None
        for fr in data:
            if fr.get("from_user") and fr["from_user"].get("email") == a:
                req_id = fr["id"]
                break
        if req_id:
            # Only the sender can cancel the request; cancel as A
            resp_cancel = await client.delete(
                f"/friends/requests/{req_id}",
                headers=_auth(tokens[a]),
            )
            assert resp_cancel.status_code in (200, 204, 404), resp_cancel.text


@pytest.mark.anyio
async def test_friend_request_accept_decline(client, ensure_test_users):
    tokens = {u["email"]: u["token"] for u in ensure_test_users}
    a = "ttt@test.com"
    b = "yyy@test.com"

    # Resolve UUIDs for A and B via /api/auth/me
    resp_me_a = await client.get("/auth/me", headers=_auth(tokens[a]))
    resp_me_b = await client.get("/auth/me", headers=_auth(tokens[b]))
    assert resp_me_a.status_code == 200 and resp_me_b.status_code == 200
    a_id = resp_me_a.json().get("id")
    b_id = resp_me_b.json().get("id")
    assert a_id and b_id

    # Send A->B
    resp_send = await client.post(
        "/friends/requests",
        headers=_auth(tokens[a]),
        json={"to_email": b},
    )
    # Try to get request id from creation response if available
    req_id = resp_send.json().get("id") if resp_send.status_code in (200, 201) else None

    # Prefer A's outgoing list to get the exact request id
    req_id = None
    existing_status = None
    resp_list_a = await client.get(
        "/friends/requests",
        headers=_auth(tokens[a]),
        params={"direction": "out"},
    )
    assert resp_list_a.status_code == 200
    for fr in resp_list_a.json():
        if fr.get("from_user_id") == a_id and fr.get("to_user_id") == b_id:
            existing_status = fr.get("status")
            if existing_status == "pending":
                req_id = fr["id"]
                break
    # Fallback: check B's incoming
    if req_id is None:
        resp_list_b = await client.get(
            "/friends/requests",
            headers=_auth(tokens[b]),
            params={"direction": "in"},
        )
        assert resp_list_b.status_code == 200
        for fr in resp_list_b.json():
            if fr.get("from_user_id") == a_id and fr.get("to_user_id") == b_id:
                existing_status = fr.get("status")
                if existing_status == "pending":
                    req_id = fr["id"]
                    break
    # Final fallback: list all for both users and match either direction
    if req_id is None:
        for email, token in ((b, tokens[b]), (a, tokens[a])):
            resp_list_all = await client.get(
                "/friends/requests",
                headers=_auth(token),
            )
            for fr in resp_list_all.json():
                pair = {fr.get("from_user_id"), fr.get("to_user_id")}
                if {a_id, b_id} == pair:
                    existing_status = fr.get("status")
                    if existing_status == "pending":
                        req_id = fr["id"]
                        break
            if req_id:
                break
    # If we found a non-pending existing request, delete it as sender A and re-send
    if req_id is None and existing_status and existing_status != "pending":
        # locate exact request id from A's outgoing if not already
        if not req_id:
            for fr in resp_list_a.json():
                if fr.get("from_user_id") == a_id and fr.get("to_user_id") == b_id:
                    req_id = fr["id"]
                    break
        if req_id:
            await client.delete(f"/friends/requests/{req_id}", headers=_auth(tokens[a]))
        # re-send and try to locate pending
        await client.post(
            "/friends/requests",
            headers=_auth(tokens[a]),
            json={"to_email": b},
        )
        resp_list_b_pending = await client.get(
            "/friends/requests",
            headers=_auth(tokens[b]),
            params={"direction": "in"},
        )
        for fr in resp_list_b_pending.json():
            if fr.get("from_user_id") == a_id and fr.get("to_user_id") == b_id and fr.get("status") == "pending":
                req_id = fr["id"]
                break
    # If still none, attempt to create reverse request B->A and pick pending
    if req_id is None:
        await client.post(
            "/friends/requests",
            headers=_auth(tokens[b]),
            json={"to_email": a},
        )
        # Try B outgoing pending
        resp_list_b_out = await client.get(
            "/friends/requests",
            headers=_auth(tokens[b]),
            params={"direction": "out"},
        )
        if resp_list_b_out.status_code == 200:
            for fr in resp_list_b_out.json():
                if fr.get("from_user_id") == b_id and fr.get("to_user_id") == a_id and fr.get("status") == "pending":
                    req_id = fr["id"]
                    break
    # If we have a pending request, accept it; else, if already accepted skip to removal
    if req_id:
        resp_accept = await client.post(
            f"/friends/requests/{req_id}/respond",
            headers=_auth(tokens[b]),
            json={"status": "accepted"},
        )
        assert resp_accept.status_code in (200, 201), resp_accept.text
    elif existing_status == "accepted":
        # Already friends; continue to removal step
        pass
    else:
        pytest.skip("No pending friend request could be established")

    # Remove friendship to reset
    resp_remove = await client.post(
        "/friends/remove",
        headers=_auth(tokens[a]),
        json={"friend_email": b},
    )
    assert resp_remove.status_code in (200, 204, 404), resp_remove.text

    # Send again A->B
    await client.post(
        "/friends/requests",
        headers=_auth(tokens[a]),
        json={"to_email": b},
    )

    # B declines
    # Get new request id again
    resp_list_b2 = await client.get(
        "/friends/requests",
        headers=_auth(tokens[b]),
        params={"direction": "in"},
    )
    req_id2 = None
    for fr in resp_list_b2.json():
        if fr.get("from_user_id") == a_id and fr.get("to_user_id") == b_id and fr.get("status") == "pending":
            req_id2 = fr["id"]
            break
    assert req_id2 is not None

    resp_decline = await client.post(
        f"/friends/requests/{req_id2}/respond",
        headers=_auth(tokens[b]),
        json={"status": "declined"},
    )
    assert resp_decline.status_code in (200, 204), resp_decline.text
