def test_list_rooms_empty(client):
    resp = client.get("/v1/rooms")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_room_not_found(client):
    resp = client.get("/v1/rooms/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
