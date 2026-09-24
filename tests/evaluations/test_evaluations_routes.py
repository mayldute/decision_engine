from app.modules.evaluations.schemas import EvaluationCreate, EvaluationRuleCreate
from app.modules.evaluations.services import create_evaluation_service


async def test_get_all_evaluations(rule, user, authenticated_client, db_session):
    for i in range(5):
        payload = EvaluationCreate(
            input={
                "age": i,
                "country": "US",
                "amount": i,
            }
        )

        evaluation_result = EvaluationRuleCreate(
            rule_id=rule.id,
            is_matched=True,
            resulting_input={
                "age": i,
                "country": "US",
                "amount": i,
            },
        )

        await create_evaluation_service(
            payload=payload,
            evaluation_results=[evaluation_result],
            current_user=user,
            db=db_session,
        )

    response = await authenticated_client.get(
        "/api/v1/evaluations/",
        params={"skip": 0, "limit": 2},
    )

    assert response.status_code == 200

    data = response.json()

    first_ids = {item["id"] for item in data}

    response = await authenticated_client.get(
        "/api/v1/evaluations/",
        params={"skip": 2, "limit": 2},
    )

    assert response.status_code == 200

    second_data = response.json()

    assert len(second_data) == 2
    assert not first_ids.intersection(item["id"] for item in second_data)



async def test_get_evaluation(evaluation, authenticated_client):
    response = await authenticated_client.get(
        f"/api/v1/evaluations/{evaluation.id}"
    )

    assert response.status_code == 200
