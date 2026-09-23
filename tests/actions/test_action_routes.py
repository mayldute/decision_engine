async def test_create_action(authenticated_client):
    payload = {
        "field": "temperature",
        "value": 15.5,
    }

    response = await authenticated_client.post("/api/v1/actions/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["field"] == "temperature"
    assert data["value"] == 15.5
    assert "id" in data


async def test_get_all_actions_pagination(authenticated_client):
    for i in range(5):
        response = await authenticated_client.post(
            "/api/v1/actions/",
            json={
                "field": f"temperature_{i}",
                "value": i,
            },
        )
        assert response.status_code == 201

    response = await authenticated_client.get(
        "/api/v1/actions/",
        params={"skip": 0, "limit": 2},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


async def test_get_actions(authenticated_client, action_data):
    response = await authenticated_client.get(f"/api/v1/actions/{action_data['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == action_data["id"]
    assert data["field"] == "temperature"
    assert data["value"] == 15.5


async def test_update_action(authenticated_client, action_data):
    response = await authenticated_client.patch(
        f"/api/v1/actions/{action_data['id']}",
        json={"value": 5},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["field"] == "temperature"
    assert data["value"] == 5


async def test_delete_action(authenticated_client, action_data):
    response = await authenticated_client.delete(f"/api/v1/actions/{action_data['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Action successfully deleted."
    assert data["action_id"] == action_data["id"]
