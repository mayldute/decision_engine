import uuid

import pytest

from app.core.exceptions import EvaluationNotFoundError
from app.modules.evaluations.schemas import EvaluationCreate, EvaluationRuleCreate
from app.modules.evaluations.services import (
    create_evaluation_service,
    get_all_evaluations_service,
    get_evaluation_service,
)


async def test_create_evaluation(evaluation, rule):
    assert evaluation.input == {"age": 25, "country": "US", "amount": 1500}
    assert evaluation.evaluation_rules[0].rule_id == rule.id
    assert evaluation.evaluation_rules[0].is_matched is True
    assert evaluation.evaluation_rules[0].resulting_input == {"age": 10, "country": "US", "amount": 1500}


async def test_get_all_evaluations(evaluation, user, db_session):
    result = await get_all_evaluations_service(
        skip=0,
        limit=2,
        current_user=user,
        db=db_session,
    )

    assert evaluation.id in {ev.id for ev in result}


async def test_get_all_evaluations_pagination(rule, user, db_session):
    for i in range(5):
        payload = EvaluationCreate(
            input={"age": i, "country": "US", "amount": i},
        )

        evaluation_result = EvaluationRuleCreate(
            rule_id=rule.id,
            is_matched=True,
            resulting_input={"age": 10, "country": "US", "amount": 1500},
        )

        await create_evaluation_service(
            payload=payload,
            evaluation_results=[evaluation_result],
            current_user=user,
            db=db_session,
        )

    first_page = await get_all_evaluations_service(
            skip=0,
            limit=2,
            current_user=user,
            db=db_session,
        )
    
    second_page = await get_all_evaluations_service(
        skip=2,
        limit=2,
        current_user=user,
        db=db_session,
    )

    last_page = await get_all_evaluations_service(
        skip=4,
        limit=2,
        current_user=user,
        db=db_session,
    )

    assert len(first_page) == 2
    assert len(second_page) == 2
    assert len(last_page) == 1

    assert first_page[0].id not in {evaluation.id for evaluation in second_page}
    assert first_page[0].id not in {evaluation.id for evaluation in last_page}
    assert second_page[0].id not in {evaluation.id for evaluation in last_page}
    
    
async def test_get_evaluation(evaluation, rule, user, db_session):
    result = await get_evaluation_service(evaluation.id, user, db_session)

    assert result.input == {"age": 25, "country": "US", "amount": 1500}
    assert result.evaluation_rules[0].rule_id == rule.id
    assert result.evaluation_rules[0].is_matched is True
    assert result.evaluation_rules[0].resulting_input == {"age": 10, "country": "US", "amount": 1500}


async def test_get_evaluation_not_found(user, db_session):
    evaluation_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440789")

    with pytest.raises(EvaluationNotFoundError) as exc_info:
        await get_evaluation_service(evaluation_id, user, db_session)

    assert (str(evaluation_id)) in str(exc_info.value)


async def test_user_cannot_access_another_users_evaluation(
    evaluation,
    another_user,
    db_session,
):
    with pytest.raises(EvaluationNotFoundError):
        await get_evaluation_service(
            evaluation.id,
            another_user,
            db_session,
        )


async def test_get_all_evaluations_only_returns_current_users_evaluations(
    evaluation,
    another_user,
    db_session,
):
    result = await get_all_evaluations_service(
        skip=0,
        limit=20,
        current_user=another_user,
        db=db_session,
    )

    assert all(ev.id != evaluation.id for ev in result)
