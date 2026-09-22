import uuid

import pytest

from app.core.exceptions import ActionNotFoundError
from app.modules.actions.schemas import ActionUpdate, ActionCreate
from app.modules.actions.services import (
    create_action_service,
    delete_action_service,
    get_action_or_raise,
    get_action_service,
    get_all_actions_service,
    update_action_service,
)


async def test_create_action(action):
    assert action.field == "temperature"
    assert action.value == 15.5
    assert action.id is not None


async def test_get_all_actions(action, db_session):
    result = await get_all_actions_service(
        skip=0,
        limit=2,
        db=db_session,
    )

    created_action = next(act for act in result if act.id == action.id)

    assert created_action.field == "temperature"
    assert created_action.value == 15.5


async def test_get_all_actions_pagination(db_session):
    for i in range(5):
        payload = ActionCreate(
                field=f"temperature_{i}",
                value=i,
            )

        await create_action_service(payload, db_session)
        
    first_page = await get_all_actions_service(
        skip=0,
        limit=2,
        db=db_session,
    )

    second_page = await get_all_actions_service(
        skip=2,
        limit=2,
        db=db_session,
    )

    last_page = await get_all_actions_service(
        skip=4,
        limit=2,
        db=db_session,
    )

    assert len(first_page) == 2
    assert len(second_page) == 2
    assert len(last_page) == 1

    assert first_page[0].id not in {action.id for action in second_page}
    assert first_page[0].id not in {action.id for action in last_page}
    assert second_page[0].id not in {action.id for action in last_page}


async def test_get_action_or_raise(db_session):
    action_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440789")

    with pytest.raises(ActionNotFoundError) as exc_info:
        await get_action_or_raise(action_id, db_session)

    assert str(action_id) in str(exc_info.value)


async def test_get_action(action, db_session):
    result = await get_action_service(action.id, db_session)

    assert result.id == action.id
    assert result.field == "temperature"
    assert result.value == 15.5


async def test_update_action(action, db_session):
    new_data = ActionUpdate(value=5)

    result = await update_action_service(
        action.id,
        new_data,
        db_session,
    )

    assert result.field == "temperature"
    assert result.value == 5


async def test_delete_action(action, db_session):
    result = await delete_action_service(action.id, db_session)

    assert result.action_id == action.id
    assert result.message == "Action successfully deleted."
