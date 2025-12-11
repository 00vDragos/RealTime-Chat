import pytest


@pytest.mark.anyio
async def test_seed_users(ensure_test_users):
    # ensure_test_users returns list of dicts with email and token
    assert len(ensure_test_users) == 4
    emails = {u["email"] for u in ensure_test_users}
    assert emails == {"ttt@test.com", "yyy@test.com", "uuu@test.com", "iii@test.com"}
    # tokens should exist
    for u in ensure_test_users:
        assert u["token"]
