import uuid

import pytest

from app.core.exceptions import ConditionNotFoundError
from app.modules.conditions.schemas import ConditionCreate, ConditionUpdate
from app.modules.conditions.services import (
    create_condition_service,
    delete_condition_service,
    get_all_conditions_service,
    get_condition_or_raise,
    get_condition_service,
    update_condition_service,
)


async def test_create_condition(condition, db_session):
    assert condition.field == "temperature"
    assert condition.operator == ">"
    assert condition.value == 25
    assert condition.id is not None


async def test_get_all_conditions(condition, db_session):
    result = await get_all_conditions_service(
        skip=0,
        limit=2,
        db=db_session,
    )

    created_condition = next(cond for cond in result if cond.id == condition.id)

    assert created_condition.field == "temperature"
    assert created_condition.operator == ">"
    assert created_condition.value == 25


async def test_get_all_conditions_pagination(db_session):
    for i in range(5):
        payload = ConditionCreate(
            field=f"temperature_{i}",
            operator="==",
            value=i,
        )

        await create_condition_service(payload, db_session)

    first_page = await get_all_conditions_service(
        skip=0,
        limit=2,
        db=db_session,
    )

    second_page = await get_all_conditions_service(
        skip=2,
        limit=2,
        db=db_session,
    )

    last_page = await get_all_conditions_service(
        skip=4,
        limit=2,
        db=db_session,
    )

    assert len(first_page) == 2
    assert len(second_page) == 2
    assert len(last_page) == 1

    assert first_page[0].id not in {condition.id for condition in second_page}
    assert first_page[0].id not in {condition.id for condition in last_page}
    assert second_page[0].id not in {condition.id for condition in last_page}


async def test_get_condition_or_raise(db_session):
    condition_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

    with pytest.raises(ConditionNotFoundError) as exc_info:
        await get_condition_or_raise(condition_id, db_session)

    assert str(condition_id) in str(exc_info.value)


async def test_get_condition(condition, db_session):
    result = await get_condition_service(condition.id, db_session)

    assert result.id == condition.id
    assert result.field == "temperature"
    assert result.operator == ">"
    assert result.value == 25


async def test_update_condition(condition, db_session):
    new_data = ConditionUpdate(value=10)

    result = await update_condition_service(condition.id, new_data, db_session)

    assert result.field == "temperature"
    assert result.operator == ">"
    assert result.value == 10


async def test_delete_condition(condition, db_session):
    result = await delete_condition_service(condition.id, db_session)

    assert result.condition_id == condition.id
    assert result.message == "Condition successfully deleted."
