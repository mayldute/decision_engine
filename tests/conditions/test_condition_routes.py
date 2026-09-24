async def test_create_condition(authenticated_client):
    payload = {
        "field": "temperature",
        "operator": ">",
        "value": 25,
    }

    response = await authenticated_client.post("/api/v1/conditions/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["field"] == "temperature"
    assert data["operator"] == ">"
    assert data["value"] == 25
    assert "id" in data


async def test_get_all_conditions_pagination(authenticated_client):
    for i in range(5):
        response = await authenticated_client.post(
            "/api/v1/conditions/",
            json={
                "field": f"temperature_{i}",
                "operator": "==",
                "value": i,
            },
        )
        assert response.status_code == 201

    response = await authenticated_client.get(
        "/api/v1/conditions/",
        params={"skip": 0, "limit": 2},
    )

    assert response.status_code == 200

    data = response.json()

    first_ids = {item["id"] for item in data}

    response = await authenticated_client.get(
        "/api/v1/conditions/",
        params={"skip": 2, "limit": 2},
    )

    assert response.status_code == 200

    second_data = response.json()

    assert len(second_data) == 2
    assert not first_ids.intersection(item["id"] for item in second_data)


async def test_get_condition(condition_data, authenticated_client):
    response = await authenticated_client.get(
        f"/api/v1/conditions/{condition_data['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == condition_data["id"]
    assert data["field"] == "temperature"
    assert data["operator"] == ">"
    assert data["value"] == 25


async def test_update_condition(condition_data, authenticated_client):
    response = await authenticated_client.patch(
        f"/api/v1/conditions/{condition_data['id']}",
        json={"value": 10},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["field"] == "temperature"
    assert data["operator"] == ">"
    assert data["value"] == 10


async def test_delete_condition(condition_data, authenticated_client):
    response = await authenticated_client.delete(
        f"/api/v1/conditions/{condition_data['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Condition successfully deleted."
    assert data["condition_id"] == condition_data["id"]

    response = await authenticated_client.get(
        f"/api/v1/conditions/{condition_data['id']}"
    )

    assert response.status_code == 404
