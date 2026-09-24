async def test_create_rule(condition_data, action_data, authenticated_client):
    payload = {
        "name": "test_rule",
        "description": "test_rule_description",
        "logical_operator": None,
        "priority": 99,
        "is_active": True,
        "condition_ids": [condition_data["id"]],
        "action_id": action_data["id"],
    }

    response = await authenticated_client.post(
        "/api/v1/rules/",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "test_rule"
    assert data["description"] == "test_rule_description"
    assert data["logical_operator"] is None
    assert data["priority"] == 99
    assert data["is_active"] is True

    condition = data["conditions"][0]

    assert condition["id"] == condition_data["id"]
    assert condition["field"] == condition_data["field"]
    assert condition["operator"] == condition_data["operator"]
    assert condition["value"] == condition_data["value"]

    assert data["action"]["id"] == action_data["id"]


async def test_get_all_rules_pagination(
    condition_data, action_data, authenticated_client
):
    for _i in range(5):
        response = await authenticated_client.post(
            "/api/v1/rules/",
            json={
                "name": "test_rule",
                "description": "test_rule_description",
                "logical_operator": None,
                "priority": 99,
                "is_active": True,
                "condition_ids": [condition_data["id"]],
                "action_id": action_data["id"],
            },
        )
        assert response.status_code == 201

    response = await authenticated_client.get(
        "/api/v1/rules/",
        params={"skip": 0, "limit": 2},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    first_ids = {item["id"] for item in data}

    response = await authenticated_client.get(
        "/api/v1/rules/",
        params={"skip": 2, "limit": 2},
    )

    assert response.status_code == 200

    second_data = response.json()

    assert len(second_data) == 2
    assert not first_ids.intersection(item["id"] for item in second_data)


async def test_get_rule(rule_data, authenticated_client):
    response = await authenticated_client.get(f"/api/v1/rules/{rule_data['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == rule_data["id"]
    assert data["name"] == "test_rule"
    assert data["description"] == "test_rule_description"
    assert data["logical_operator"] is None
    assert data["priority"] == 99
    assert data["is_active"] is True

    condition = data["conditions"][0]
    expected_condition = rule_data["conditions"][0]

    assert condition == expected_condition
    assert data["action"]["id"] == rule_data["action"]["id"]


async def test_update_rule(rule_data, authenticated_client):
    response = await authenticated_client.patch(
        f"/api/v1/rules/{rule_data['id']}",
        json={"name": "new_test_rule"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "new_test_rule"
    assert data["description"] == "test_rule_description"
    assert data["logical_operator"] is None
    assert data["priority"] == 99
    assert data["is_active"] is True

    condition = data["conditions"][0]
    expected_condition = rule_data["conditions"][0]

    assert condition == expected_condition
    assert data["action"]["id"] == rule_data["action"]["id"]


async def test_delete_rule(rule_data, authenticated_client):
    response = await authenticated_client.delete(f"/api/v1/rules/{rule_data['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Rule successfully deleted."
    assert data["rule_id"] == rule_data["id"]

    response = await authenticated_client.get(f"/api/v1/rules/{rule_data['id']}")

    assert response.status_code == 404
