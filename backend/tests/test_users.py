def test_wallet_challenge(client):
    resp = client.get("/v1/users/challenge", params={"wallet_address": "4Nd1mBQtrMJVYVfKf2PX98ej9cn6gBV6tVWN99tCMTBQ"})
    assert resp.status_code == 200
    data = resp.json()
    assert "nonce" in data
    assert "expires_at" in data


def test_onboard_invalid_nonce(client):
    resp = client.post("/v1/users/onboard", json={
        "wallet_address": "4Nd1mBQtrMJVYVfKf2PX98ej9cn6gBV6tVWN99tCMTBQ",
        "signature": "fake_sig",
        "nonce": "bad_nonce",
    })
    assert resp.status_code == 401
