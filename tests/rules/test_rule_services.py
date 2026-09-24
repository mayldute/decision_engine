import uuid

import pytest

from app.core.exceptions import (
    RuleMustHaveConditionError,
    RuleNoLogicalOperator,
    RuleNotFoundError,
)
from app.modules.actions.schemas import ActionCreate
from app.modules.actions.services import create_action_service
from app.modules.conditions.schemas import ConditionCreate
from app.modules.conditions.services import create_condition_service
from app.modules.rules.schemas import RuleCreate, RuleUpdate
from app.modules.rules.services import (
    create_rule_service,
    delete_rule_service,
    get_all_rules_service,
    get_rule_or_raise,
    get_rule_service,
    update_rule_service,
)


async def test_create_rule_one_condition(condition, action, user, db_session):
    payload = RuleCreate(
        name="test_rule",
        description="test_rule_description",
        logical_operator=None,
        priority=99,
        is_active=True,
        condition_ids=[condition.id],
        action_id=action.id,
    )

    created_rule = await create_rule_service(payload, user, db_session)

    assert created_rule.name == "test_rule"
    assert created_rule.description == "test_rule_description"
    assert created_rule.logical_operator is None
    assert created_rule.priority == 99
    assert created_rule.is_active is True
    assert len(created_rule.conditions) == 1
    assert created_rule.conditions[0].id == condition.id
    assert created_rule.action.id == action.id


async def test_create_rule(action, rule):
    assert rule.name == "test_rule"
    assert rule.description == "test_rule_description"
    assert rule.logical_operator == "AND"
    assert rule.priority == 99
    assert rule.is_active is True
    assert len(rule.conditions) == 3

    for i, condition in enumerate(rule.conditions):
        assert condition.field == f"temperature_{i}"
        assert condition.operator == "=="
        assert condition.value == i

    assert rule.action.id == action.id


async def test_get_all_rules(rule, action, user, db_session):
    result = await get_all_rules_service(
        skip=0,
        limit=2,
        current_user=user,
        db=db_session,
    )

    created_rule = next(r for r in result if r.id == rule.id)

    assert created_rule.name == "test_rule"
    assert created_rule.description == "test_rule_description"
    assert created_rule.logical_operator == "AND"
    assert created_rule.priority == 99
    assert created_rule.is_active is True
    assert len(created_rule.conditions) == 3

    for i, condition in enumerate(created_rule.conditions):
        assert condition.field == f"temperature_{i}"
        assert condition.operator == "=="
        assert condition.value == i

    assert created_rule.action.id == action.id


async def test_get_all_rules_pagination(user, condition, action, db_session):
    for i in range(5):
        payload = RuleCreate(
            name=f"test_rule_{i}",
            description=f"test_rule_description_{i}",
            logical_operator=None,
            priority=i,
            is_active=True,
            condition_ids=[condition.id],
            action_id=action.id,
        )

        await create_rule_service(payload, user, db_session)

    first_page = await get_all_rules_service(
        skip=0,
        limit=2,
        current_user=user,
        db=db_session,
    )

    second_page = await get_all_rules_service(
        skip=2,
        limit=2,
        current_user=user,
        db=db_session,
    )

    last_page = await get_all_rules_service(
        skip=4,
        limit=2,
        current_user=user,
        db=db_session,
    )

    assert len(first_page) == 2
    assert len(second_page) == 2
    assert len(last_page) == 1

    assert first_page[0].id not in {rule.id for rule in second_page}
    assert first_page[0].id not in {rule.id for rule in last_page}
    assert second_page[0].id not in {rule.id for rule in last_page}


async def test_get_rule_or_raise(user, db_session):
    rule_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

    with pytest.raises(RuleNotFoundError) as exc_info:
        await get_rule_or_raise(rule_id, user, db_session)

    assert str(rule_id) in str(exc_info.value)


async def test_update_rule_from_another_user(
    rule,
    another_user,
    db_session,
):
    new_data = RuleUpdate(name="hacked_rule")

    with pytest.raises(RuleNotFoundError):
        await update_rule_service(
            rule.id,
            new_data,
            another_user,
            db_session,
        )


async def test_get_rule(rule, action, user, db_session):
    result = await get_rule_service(rule.id, user, db_session)

    assert result.name == "test_rule"
    assert result.description == "test_rule_description"
    assert result.logical_operator == "AND"
    assert result.priority == 99
    assert result.is_active is True
    assert len(result.conditions) == 3

    for i, condition in enumerate(result.conditions):
        assert condition.field == f"temperature_{i}"
        assert condition.operator == "=="
        assert condition.value == i

    assert result.action.id == action.id


async def test_update_service(rule, action, user, db_session):
    new_data = RuleUpdate(name="new_test_rule")

    result = await update_rule_service(rule.id, new_data, user, db_session)

    assert result.name == "new_test_rule"
    assert result.description == "test_rule_description"
    assert result.logical_operator == "AND"
    assert result.priority == 99
    assert result.is_active is True
    assert len(result.conditions) == 3

    for i, condition in enumerate(result.conditions):
        assert condition.field == f"temperature_{i}"
        assert condition.operator == "=="
        assert condition.value == i

    assert result.action.id == action.id


async def test_update_rule_conditions(rule, user, db_session):
    new_condition = await create_condition_service(
        payload=ConditionCreate(
            field="age",
            operator=">",
            value=18,
        ),
        current_user=user,
        db=db_session,
    )

    new_data = RuleUpdate(condition_ids=[new_condition.id])

    result = await update_rule_service(
        rule.id,
        new_data,
        user,
        db_session,
    )

    assert len(result.conditions) == 1
    assert result.conditions[0].id == new_condition.id
    assert result.logical_operator is None


async def test_update_rule_with_new_conditions(rule, user, db_session):
    new_data = RuleUpdate(
        new_conditions=[
            ConditionCreate(
                field="age",
                operator=">",
                value=18,
            ),
            ConditionCreate(
                field="country",
                operator="==",
                value="US",
            ),
        ],
        logical_operator="OR",
    )

    result = await update_rule_service(
        rule.id,
        new_data,
        user,
        db_session,
    )

    assert len(result.conditions) == 2

    assert result.conditions[0].field == "age"
    assert result.conditions[0].operator == ">"
    assert result.conditions[0].value == 18

    assert result.conditions[1].field == "country"
    assert result.conditions[1].operator == "=="
    assert result.conditions[1].value == "US"

    assert result.logical_operator == "OR"


async def test_update_rule_action(rule, user, db_session):
    new_action = await create_action_service(
        payload=ActionCreate(
            field="temperature",
            value=30,
        ),
        current_user=user,
        db=db_session,
    )

    new_data = RuleUpdate(action_id=new_action.id)

    result = await update_rule_service(
        rule.id,
        new_data,
        user,
        db_session,
    )

    assert result.action.id == new_action.id
    assert result.action.field == "temperature"
    assert result.action.value == 30


async def test_update_rule_with_new_action(rule, user, db_session):
    new_data = RuleUpdate(
        new_action=ActionCreate(
            field="status",
            value="approved",
        )
    )

    result = await update_rule_service(
        rule.id,
        new_data,
        user,
        db_session,
    )

    assert result.action.field == "status"
    assert result.action.value == "approved"


async def test_update_rule_with_empty_condition_ids(rule, user, db_session):
    new_data = RuleUpdate(condition_ids=[])

    with pytest.raises(RuleMustHaveConditionError):
        await update_rule_service(
            rule.id,
            new_data,
            user,
            db_session,
        )


async def test_update_rule_with_empty_new_conditions(rule, user, db_session):
    new_data = RuleUpdate(new_conditions=[])

    with pytest.raises(RuleMustHaveConditionError):
        await update_rule_service(
            rule.id,
            new_data,
            user,
            db_session,
        )


async def test_update_rule_multiple_conditions_without_logical_operator(
    rule,
    user,
    db_session,
):
    new_condition = await create_condition_service(
        payload=ConditionCreate(
            field="age",
            operator=">",
            value=18,
        ),
        current_user=user,
        db=db_session,
    )

    new_data = RuleUpdate(
        condition_ids=[
            rule.conditions[0].id,
            new_condition.id,
        ],
        logical_operator=None,
    )

    with pytest.raises(RuleNoLogicalOperator):
        await update_rule_service(
            rule.id,
            new_data,
            user,
            db_session,
        )


async def test_update_rule_one_condition_clears_logical_operator(
    rule,
    user,
    db_session,
):
    new_data = RuleUpdate(
        condition_ids=[rule.conditions[0].id],
    )

    result = await update_rule_service(
        rule.id,
        new_data,
        user,
        db_session,
    )

    assert len(result.conditions) == 1
    assert result.logical_operator is None


async def test_delete_rule(rule, user, db_session):
    result = await delete_rule_service(rule.id, user, db_session)

    assert result.rule_id == rule.id
    assert result.message == "Rule successfully deleted."
